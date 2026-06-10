import fs from 'node:fs';
import path from 'node:path';

const root = process.argv[2];
if (!root) {
  throw new Error('Usage: node verify-photo-upload-size.mjs <repo-root>');
}

const repoRoot = path.resolve(root);
const frontendUploadPath = path.join(repoRoot, 'kaipai-frontend', 'src', 'utils', 'upload.ts');
const backendCosPath = path.join(repoRoot, 'kaipaile-server', 'src', 'main', 'java', 'com', 'kaipai', 'integration', 'storage', 'CosUtil.java');
const backendFileControllerPath = path.join(repoRoot, 'kaipaile-server', 'src', 'main', 'java', 'com', 'kaipai', 'controller', 'api', 'file', 'FileController.java');

const frontendUpload = fs.readFileSync(frontendUploadPath, 'utf8');
const backendCos = fs.readFileSync(backendCosPath, 'utf8');
const backendFileController = fs.readFileSync(backendFileControllerPath, 'utf8');

function assertIncludes(source, expected, label) {
  if (!source.includes(expected)) {
    throw new Error(`${label} missing: ${expected}`);
  }
}

function assertNotIncludes(source, unexpected, label) {
  if (source.includes(unexpected)) {
    throw new Error(`${label} still contains: ${unexpected}`);
  }
}

assertIncludes(frontendUpload, 'photo: 10 * 1024 * 1024', 'frontend photo size limit');
assertIncludes(frontendUpload, "photo: '作品图片不能超过10MB'", 'frontend photo size message');
assertIncludes(frontendUpload, 'avatar: 2 * 1024 * 1024', 'frontend avatar limit');
assertIncludes(frontendUpload, 'license: 5 * 1024 * 1024', 'frontend license limit');
assertIncludes(frontendUpload, 'pdf: 20 * 1024 * 1024', 'frontend pdf limit');
assertIncludes(frontendUpload, 'video: 100 * 1024 * 1024', 'frontend video limit');
assertNotIncludes(frontendUpload, "photo: '作品图片不能超过5MB'", 'frontend photo size message');

assertIncludes(backendCos, 'private static final long PHOTO_MAX_SIZE = 10 * MB;', 'backend photo size limit');
assertIncludes(backendCos, 'case "photo" -> "作品图片不能超过10MB";', 'backend photo size message');
assertIncludes(backendCos, 'default -> "图片大小不能超过10MB";', 'backend default image size message');
assertIncludes(backendCos, 'private static final long AVATAR_MAX_SIZE = 2 * MB;', 'backend avatar limit');
assertIncludes(backendCos, 'private static final long LICENSE_MAX_SIZE = 5 * MB;', 'backend license limit');
assertIncludes(backendCos, 'private static final long PDF_MAX_SIZE = 20 * MB;', 'backend pdf limit');
assertIncludes(backendCos, 'private static final long VIDEO_MAX_SIZE = 100 * MB;', 'backend video limit');
assertIncludes(backendCos, 'case "license" -> "营业执照图片不能超过5MB";', 'backend license size message');
assertNotIncludes(backendCos, 'case "photo" -> "作品图片不能超过5MB";', 'backend photo size message');

assertIncludes(backendFileController, '每张建议不超过 10MB', 'backend photo upload API docs');
assertNotIncludes(backendFileController, '每张建议不超过 5MB', 'backend photo upload API docs');

console.log('Photo upload size verification passed.');
