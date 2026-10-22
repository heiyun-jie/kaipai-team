package com.kaipai.ops;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.kaipai.KaipaiApplication;
import com.kaipai.common.config.TencentCloudProperties;
import com.qcloud.cos.COSClient;
import com.qcloud.cos.model.ListObjectsRequest;
import com.qcloud.cos.model.ObjectListing;
import com.qcloud.cos.model.ObjectMetadata;
import com.qcloud.cos.model.PutObjectRequest;
import com.qcloud.cos.model.CannedAccessControlList;
import com.qcloud.cos.model.CreateBucketRequest;
import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import javax.sql.DataSource;
import org.springframework.boot.WebApplicationType;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.context.ConfigurableApplicationContext;

public final class LegacyMediaBackfillTool {
    private static final long PHOTO_MAX = 10L * 1024 * 1024;
    private static final long VIDEO_MAX = 100L * 1024 * 1024;
    private static final TypeReference<List<String>> STRING_LIST = new TypeReference<>() {};

    private LegacyMediaBackfillTool() {}

    public static void main(String[] args) throws Exception {
        Options options = Options.parse(args);
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("candidateId", options.candidateId());
        result.put("manifestSha256", options.manifestSha256());
        result.put("environment", options.environment());
        result.put("mode", options.mode());

        try (ConfigurableApplicationContext context = new SpringApplicationBuilder(KaipaiApplication.class)
                .web(WebApplicationType.NONE)
                .profiles("test")
                .properties(
                        "spring.main.banner-mode=off",
                        "spring.main.lazy-initialization=true",
                        "logging.level.root=WARN",
                        "spring.task.scheduling.enabled=false")
                .run()) {
            DataSource dataSource = context.getBean(DataSource.class);
            COSClient cos = context.getBean(COSClient.class);
            TencentCloudProperties properties = context.getBean(TencentCloudProperties.class);
            ObjectMapper mapper = context.getBean(ObjectMapper.class);

            String configuredTarget = trim(properties.getCos().getPrivateBucketName());
            require(Objects.equals(configuredTarget, options.targetBucket()), "target bucket does not match test runtime");
            require(configuredTarget != null && configuredTarget.toLowerCase(Locale.ROOT).contains("test"),
                    "test bucket name must be explicitly test-scoped");
            if (options.isEnsureBucket()) {
                boolean created = false;
                if (!cos.doesBucketExist(configuredTarget)) {
                    CreateBucketRequest request = new CreateBucketRequest(configuredTarget);
                    request.setCannedAcl(CannedAccessControlList.Private);
                    cos.createBucket(request);
                    created = true;
                }
                cos.setBucketAcl(configuredTarget, CannedAccessControlList.Private);
                result.put("bucketCreated", created);
                result.put("privateAclApplied", true);
                result.put("passed", cos.doesBucketExist(configuredTarget));
                System.out.println("BACKFILL_RESULT_JSON=" + mapper.writeValueAsString(result));
                return;
            }
            require(cos.doesBucketExist(configuredTarget), "test bucket does not exist or is not accessible");

            Scan scan = scan(dataSource, mapper);
            Set<String> protectedSourceBuckets = sourceBuckets(scan.items());
            protectedSourceBuckets.remove(configuredTarget);
            require(!protectedSourceBuckets.isEmpty(), "no production source bucket was identified");
            Map<String, BucketFingerprint> productionBefore = fingerprint(cos, protectedSourceBuckets);
            result.put("sourceCounts", scan.sourceCounts());
            result.put("itemCount", scan.items().size());
            result.put("uniqueSourceKeyCount", scan.items().stream().map(SourceItem::sourceKey).distinct().count());
            result.put("protectedSourceBucketCount", protectedSourceBuckets.size());

            Counters counters = new Counters();
            List<Map<String, Object>> failures = new ArrayList<>();
            HttpClient client = HttpClient.newBuilder()
                    .connectTimeout(Duration.ofSeconds(10))
                    .followRedirects(HttpClient.Redirect.NORMAL)
                    .build();
            Set<String> processed = new LinkedHashSet<>();

            for (SourceItem item : scan.items()) {
                if (!processed.add(item.sourceKey())) {
                    counters.duplicates++;
                    continue;
                }
                try {
                    Downloaded downloaded = download(client, item);
                    counters.readable++;
                    if (options.isApply()) {
                        applyItem(dataSource, cos, configuredTarget, item, downloaded, counters);
                    }
                } catch (Exception error) {
                    counters.failed++;
                    failures.add(failure(item, classify(error)));
                }
            }

            Map<String, BucketFingerprint> productionAfter = fingerprint(cos, protectedSourceBuckets);
            require(productionBefore.equals(productionAfter), "production bucket fingerprint changed");
            result.put("productionBucketUnchanged", true);
            result.put("counters", counters.asMap());
            result.put("failures", failures);
            result.put("passed", failures.isEmpty());
            System.out.println("BACKFILL_RESULT_JSON=" + mapper.writeValueAsString(result));
            if (!failures.isEmpty()) {
                throw new IllegalStateException("legacy media backfill has unresolved failures");
            }
        }
    }

    private static Scan scan(DataSource dataSource, ObjectMapper mapper) throws Exception {
        List<SourceItem> items = new ArrayList<>();
        Map<String, Integer> counts = new LinkedHashMap<>();
        counts.put("userAvatarNonEmpty", 0);
        counts.put("profileAvatarNonEmpty", 0);
        counts.put("profilePhotoNonEmpty", 0);
        counts.put("profileVideoNonEmpty", 0);

        String sql = """
                SELECT p.actor_profile_id, p.user_id, p.avatar_url, p.photo_urls, p.video_url,
                       u.avatar_url AS user_avatar_url
                FROM actor_profile p
                JOIN user u ON u.user_id = p.user_id AND u.deleted = 0
                WHERE p.deleted = 0
                ORDER BY p.actor_profile_id
                """;
        try (Connection connection = dataSource.getConnection();
             PreparedStatement statement = connection.prepareStatement(sql);
             ResultSet rows = statement.executeQuery()) {
            while (rows.next()) {
                long profileId = rows.getLong("actor_profile_id");
                long userId = rows.getLong("user_id");
                String profileAvatar = trim(rows.getString("avatar_url"));
                String userAvatar = trim(rows.getString("user_avatar_url"));
                String photosJson = trim(rows.getString("photo_urls"));
                String video = trim(rows.getString("video_url"));

                if (profileAvatar != null) counts.compute("profileAvatarNonEmpty", (key, value) -> value + 1);
                if (userAvatar != null) counts.compute("userAvatarNonEmpty", (key, value) -> value + 1);
                String selectedAvatar = profileAvatar != null ? profileAvatar : userAvatar;
                if (selectedAvatar != null) {
                    items.add(SourceItem.of(profileId, userId, "avatar", "photo", "portrait",
                            "avatar", 0, selectedAvatar));
                }

                if (photosJson != null && !"[]".equals(photosJson) && !"null".equalsIgnoreCase(photosJson)) {
                    List<String> photos;
                    try {
                        photos = mapper.readValue(photosJson, STRING_LIST);
                    } catch (Exception error) {
                        throw new IllegalStateException("INVALID_PHOTO_JSON profile=" + profileId);
                    }
                    int sort = 0;
                    for (String photo : photos) {
                        String normalized = trim(photo);
                        if (normalized == null) continue;
                        sort++;
                        counts.compute("profilePhotoNonEmpty", (key, value) -> value + 1);
                        items.add(SourceItem.of(profileId, userId, "photo_urls", "photo", "lifestyle",
                                "public_photo", sort, normalized));
                    }
                }
                if (video != null) {
                    counts.compute("profileVideoNonEmpty", (key, value) -> value + 1);
                    items.add(SourceItem.of(profileId, userId, "video_url", "video", "self_intro",
                            "public_video", 1, video));
                }
            }
        }
        items.sort(Comparator.comparingLong(SourceItem::profileId)
                .thenComparing(SourceItem::sourceField)
                .thenComparingInt(SourceItem::sortNo));
        return new Scan(items, counts);
    }

    private static Downloaded download(HttpClient client, SourceItem item) throws Exception {
        URI uri = URI.create(item.url());
        require("https".equalsIgnoreCase(uri.getScheme()), "UNTRUSTED_SCHEME");
        require(uri.getUserInfo() == null, "URL_USERINFO_FORBIDDEN");
        String host = uri.getHost() == null ? "" : uri.getHost().toLowerCase(Locale.ROOT);
        require(host.endsWith(".myqcloud.com") || host.equals("myqcloud.com")
                        || host.endsWith(".kplyyk.com") || host.equals("kplyyk.com"),
                "UNTRUSTED_HOST");
        long max = "photo".equals(item.mediaType()) ? PHOTO_MAX : VIDEO_MAX;
        HttpRequest request = HttpRequest.newBuilder(uri)
                .timeout(Duration.ofSeconds(60))
                .header("User-Agent", "kaipai-legacy-media-backfill/1")
                .GET()
                .build();
        HttpResponse<InputStream> response = client.send(request, HttpResponse.BodyHandlers.ofInputStream());
        require(response.statusCode() >= 200 && response.statusCode() < 300, "SOURCE_HTTP_" + response.statusCode());
        byte[] bytes;
        try (InputStream input = response.body()) {
            bytes = input.readNBytes((int) max + 1);
        }
        require(bytes.length > 0, "SOURCE_EMPTY");
        require(bytes.length <= max, "SOURCE_TOO_LARGE");
        String headerMime = response.headers().firstValue("Content-Type").orElse("").split(";", 2)[0]
                .trim().toLowerCase(Locale.ROOT);
        String mime = detectMime(bytes, item.mediaType(), headerMime);
        String extension = extension(mime);
        return new Downloaded(bytes, mime, extension);
    }

    private static String detectMime(byte[] bytes, String mediaType, String headerMime) {
        if ("photo".equals(mediaType)) {
            if (starts(bytes, 0xff, 0xd8, 0xff)) return "image/jpeg";
            if (starts(bytes, 0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a)) return "image/png";
            if (ascii(bytes, 0, "GIF87a") || ascii(bytes, 0, "GIF89a")) return "image/gif";
            if (ascii(bytes, 0, "RIFF") && ascii(bytes, 8, "WEBP")) return "image/webp";
            throw new IllegalStateException("PHOTO_MAGIC_INVALID");
        }
        if (bytes.length >= 12 && ascii(bytes, 4, "ftyp")) return "video/mp4";
        if (ascii(bytes, 0, "RIFF") && ascii(bytes, 8, "AVI ")) return "video/x-msvideo";
        if (headerMime.startsWith("video/")) return headerMime;
        throw new IllegalStateException("VIDEO_MAGIC_INVALID");
    }

    private static void applyItem(
            DataSource dataSource,
            COSClient cos,
            String bucket,
            SourceItem item,
            Downloaded downloaded,
            Counters counters) throws Exception {
        String objectKey = "actor-private/migration/" + item.userId() + "/" + item.mediaType()
                + "/" + item.sourceKey() + "." + downloaded.extension();
        boolean objectExists = cos.doesObjectExist(bucket, objectKey);
        if (!objectExists) {
            ObjectMetadata metadata = new ObjectMetadata();
            metadata.setContentLength(downloaded.bytes().length);
            metadata.setContentType(downloaded.mime());
            cos.putObject(new PutObjectRequest(bucket, objectKey,
                    new ByteArrayInputStream(downloaded.bytes()), metadata));
            counters.objectsCreated++;
        } else {
            ObjectMetadata metadata = cos.getObjectMetadata(bucket, objectKey);
            require(metadata.getContentLength() == downloaded.bytes().length, "TARGET_OBJECT_CONFLICT");
            counters.objectsReused++;
        }

        try (Connection connection = dataSource.getConnection()) {
            connection.setAutoCommit(false);
            try {
                Long assetId = findAsset(connection, bucket, objectKey);
                if (assetId == null) {
                    assetId = insertAsset(connection, bucket, objectKey, item, downloaded);
                    counters.assetsCreated++;
                } else {
                    counters.assetsReused++;
                }
                if ("avatar".equals(item.usageCode())) {
                    int updated = updateAvatar(connection, item, assetId);
                    counters.relationsCreated += updated;
                    counters.relationsReused += updated == 0 ? 1 : 0;
                } else {
                    int inserted = insertProfileRelation(connection, item, assetId);
                    counters.relationsCreated += inserted;
                    counters.relationsReused += inserted == 0 ? 1 : 0;
                }
                connection.commit();
            } catch (Exception error) {
                connection.rollback();
                throw error;
            } finally {
                connection.setAutoCommit(true);
            }
        }
    }

    private static Long findAsset(Connection connection, String bucket, String objectKey) throws Exception {
        String sql = "SELECT asset_id FROM actor_media_asset WHERE storage_provider='cos' AND bucket_code=? AND object_key=? AND deleted=0 LIMIT 1";
        try (PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setString(1, bucket);
            statement.setString(2, objectKey);
            try (ResultSet rows = statement.executeQuery()) {
                return rows.next() ? rows.getLong(1) : null;
            }
        }
    }

    private static long insertAsset(
            Connection connection,
            String bucket,
            String objectKey,
            SourceItem item,
            Downloaded downloaded) throws Exception {
        String sql = """
                INSERT INTO actor_media_asset (
                  user_id, media_type, category_code, storage_provider, bucket_code, object_key,
                  original_name, mime_type, size_bytes, process_status, source_type
                ) VALUES (?, ?, ?, 'cos', ?, ?, ?, ?, ?, 'ready', 'migration')
                """;
        try (PreparedStatement statement = connection.prepareStatement(sql, PreparedStatement.RETURN_GENERATED_KEYS)) {
            statement.setLong(1, item.userId());
            statement.setString(2, item.mediaType());
            statement.setString(3, item.categoryCode());
            statement.setString(4, bucket);
            statement.setString(5, objectKey);
            statement.setString(6, "legacy-" + item.sourceHash().substring(0, 12) + "." + downloaded.extension());
            statement.setString(7, downloaded.mime());
            statement.setLong(8, downloaded.bytes().length);
            require(statement.executeUpdate() == 1, "ASSET_INSERT_FAILED");
            try (ResultSet keys = statement.getGeneratedKeys()) {
                require(keys.next(), "ASSET_ID_MISSING");
                return keys.getLong(1);
            }
        }
    }

    private static int updateAvatar(Connection connection, SourceItem item, long assetId) throws Exception {
        String sql = """
                UPDATE actor_profile SET avatar_asset_id=?
                WHERE actor_profile_id=? AND user_id=? AND deleted=0
                  AND avatar_asset_id IS NULL
                """;
        try (PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setLong(1, assetId);
            statement.setLong(2, item.profileId());
            statement.setLong(3, item.userId());
            return statement.executeUpdate();
        }
    }

    private static int insertProfileRelation(Connection connection, SourceItem item, long assetId) throws Exception {
        String sql = """
                INSERT INTO actor_profile_asset (actor_profile_id, asset_id, usage_code, sort_no)
                SELECT ?, ?, ?, ?
                WHERE NOT EXISTS (
                  SELECT 1 FROM actor_profile_asset
                  WHERE actor_profile_id=? AND asset_id=? AND usage_code=? AND deleted=0
                )
                """;
        try (PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setLong(1, item.profileId());
            statement.setLong(2, assetId);
            statement.setString(3, item.usageCode());
            statement.setInt(4, item.sortNo());
            statement.setLong(5, item.profileId());
            statement.setLong(6, assetId);
            statement.setString(7, item.usageCode());
            return statement.executeUpdate();
        }
    }

    private static BucketFingerprint fingerprint(COSClient cos, String bucket) {
        require(bucket != null, "production bucket is not configured");
        long count = 0;
        long bytes = 0;
        MessageDigest digest = sha256Digest();
        ListObjectsRequest request = new ListObjectsRequest();
        request.setBucketName(bucket);
        request.setMaxKeys(1000);
        ObjectListing page = cos.listObjects(request);
        while (true) {
            for (var summary : page.getObjectSummaries()) {
                count++;
                bytes += summary.getSize();
                digest.update(summary.getKey().getBytes(StandardCharsets.UTF_8));
                digest.update(Long.toString(summary.getSize()).getBytes(StandardCharsets.UTF_8));
                if (summary.getETag() != null) digest.update(summary.getETag().getBytes(StandardCharsets.UTF_8));
            }
            if (!page.isTruncated()) break;
            page = cos.listNextBatchOfObjects(page);
        }
        return new BucketFingerprint(count, bytes, HexFormat.of().formatHex(digest.digest()));
    }

    private static Map<String, BucketFingerprint> fingerprint(COSClient cos, Set<String> buckets) {
        Map<String, BucketFingerprint> result = new LinkedHashMap<>();
        for (String bucket : buckets.stream().sorted().toList()) {
            result.put(bucket, fingerprint(cos, bucket));
        }
        return result;
    }

    private static Set<String> sourceBuckets(List<SourceItem> items) {
        Set<String> result = new LinkedHashSet<>();
        for (SourceItem item : items) {
            URI uri = URI.create(item.url());
            String host = uri.getHost();
            if (host == null) continue;
            String lower = host.toLowerCase(Locale.ROOT);
            int marker = lower.indexOf(".cos.");
            if (marker > 0) result.add(lower.substring(0, marker));
        }
        return result;
    }

    private static Map<String, Object> failure(SourceItem item, String code) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("profileId", item.profileId());
        result.put("userId", item.userId());
        result.put("sourceField", item.sourceField());
        result.put("sourceSha256", item.sourceHash());
        result.put("failureCode", code);
        return result;
    }

    private static String classify(Exception error) {
        String message = error.getMessage();
        if (message == null || message.isBlank()) return error.getClass().getSimpleName();
        int space = message.indexOf(' ');
        return (space > 0 ? message.substring(0, space) : message).replaceAll("[^A-Za-z0-9_-]", "_");
    }

    private static boolean starts(byte[] bytes, int... expected) {
        if (bytes.length < expected.length) return false;
        for (int index = 0; index < expected.length; index++) {
            if ((bytes[index] & 0xff) != expected[index]) return false;
        }
        return true;
    }

    private static boolean ascii(byte[] bytes, int offset, String value) {
        byte[] expected = value.getBytes(StandardCharsets.US_ASCII);
        if (bytes.length < offset + expected.length) return false;
        for (int index = 0; index < expected.length; index++) {
            if (bytes[offset + index] != expected[index]) return false;
        }
        return true;
    }

    private static String extension(String mime) {
        return switch (mime) {
            case "image/jpeg" -> "jpg";
            case "image/png" -> "png";
            case "image/gif" -> "gif";
            case "image/webp" -> "webp";
            case "video/x-msvideo" -> "avi";
            default -> "mp4";
        };
    }

    private static MessageDigest sha256Digest() {
        try {
            return MessageDigest.getInstance("SHA-256");
        } catch (Exception error) {
            throw new IllegalStateException(error);
        }
    }

    private static String sha256(String value) {
        return HexFormat.of().formatHex(sha256Digest().digest(value.getBytes(StandardCharsets.UTF_8)));
    }

    private static String trim(String value) {
        if (value == null || value.trim().isEmpty()) return null;
        return value.trim();
    }

    private static void require(boolean condition, String message) {
        if (!condition) throw new IllegalStateException(message);
    }

    private record Scan(List<SourceItem> items, Map<String, Integer> sourceCounts) {}
    private record Downloaded(byte[] bytes, String mime, String extension) {}
    private record BucketFingerprint(long objectCount, long totalBytes, String stableHash) {}

    private record SourceItem(
            long profileId,
            long userId,
            String sourceField,
            String mediaType,
            String categoryCode,
            String usageCode,
            int sortNo,
            String url,
            String sourceHash,
            String sourceKey) {
        static SourceItem of(
                long profileId,
                long userId,
                String sourceField,
                String mediaType,
                String categoryCode,
                String usageCode,
                int sortNo,
                String url) {
            String normalized = url.trim();
            String sourceHash = sha256(normalized);
            String sourceKey = sha256(userId + "|" + sourceField + "|" + normalized);
            return new SourceItem(profileId, userId, sourceField, mediaType, categoryCode,
                    usageCode, sortNo, normalized, sourceHash, sourceKey);
        }
    }

    private static final class Counters {
        long readable;
        long duplicates;
        long failed;
        long objectsCreated;
        long objectsReused;
        long assetsCreated;
        long assetsReused;
        long relationsCreated;
        long relationsReused;

        Map<String, Long> asMap() {
            Map<String, Long> result = new LinkedHashMap<>();
            result.put("readable", readable);
            result.put("duplicates", duplicates);
            result.put("failed", failed);
            result.put("objectsCreated", objectsCreated);
            result.put("objectsReused", objectsReused);
            result.put("assetsCreated", assetsCreated);
            result.put("assetsReused", assetsReused);
            result.put("relationsCreated", relationsCreated);
            result.put("relationsReused", relationsReused);
            return result;
        }
    }

    private record Options(
            String candidateId,
            String manifestSha256,
            String environment,
            String mode,
            String targetBucket) {
        static Options parse(String[] args) {
            Map<String, String> values = new LinkedHashMap<>();
            for (int index = 0; index < args.length; index += 2) {
                require(index + 1 < args.length, "option value is missing");
                values.put(args[index], args[index + 1]);
            }
            String candidateId = values.get("--candidate-id");
            String manifest = values.get("--manifest-sha256");
            String environment = values.get("--environment");
            String mode = values.get("--mode");
            String bucket = values.get("--target-bucket");
            require(candidateId != null && candidateId.matches("[0-9]{8}-[0-9]{4,6}-v3-draft"), "invalid candidate id");
            require(manifest != null && manifest.matches("[0-9A-Fa-f]{64}"), "invalid manifest sha256");
            require("test".equals(environment), "only the test environment is allowed");
            require("ensure-bucket".equals(mode) || "dry-run".equals(mode) || "apply".equals(mode),
                    "mode must be ensure-bucket, dry-run or apply");
            require(bucket != null && !bucket.isBlank(), "target bucket is required");
            return new Options(candidateId, manifest.toLowerCase(Locale.ROOT), environment, mode, bucket);
        }

        boolean isApply() {
            return "apply".equals(mode);
        }

        boolean isEnsureBucket() {
            return "ensure-bucket".equals(mode);
        }
    }
}
