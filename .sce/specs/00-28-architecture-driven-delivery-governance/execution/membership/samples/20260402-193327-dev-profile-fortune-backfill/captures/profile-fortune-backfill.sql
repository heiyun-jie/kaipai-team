USE kaipai_dev;
SET NAMES utf8mb4;
UPDATE actor_profile
SET real_name='Smoke User',
    is_certified=b'1',
    phone='13800138000',
    birth_hour='午时'
WHERE user_id=10000 AND deleted=0;

INSERT INTO fortune_report (
  user_id, report_month, zodiac_animal, zodiac_fortune, constellation, constellation_fortune,
  ziwei_star, ziwei_profile, lucky_color, lucky_color_name, lucky_color_interpretation,
  lucky_number, lucky_number_interpretation, birth_hour, source_type, raw_payload,
  version, deleted, rid, create_user_id, create_user_name, create_time, update_user_id, update_user_name, last_update
) VALUES (
  10000, '2026-04-01', 'horse', '{"keyword": "突破", "readings": ["本月适合主动争取更有反差的角色。", "越明确的表演标签越容易被导演记住。", "试镜前多做一版情绪层次准备。"]}',
  'leo', '{"keyword": "表现力", "readings": ["镜头前的自信会成为你的武器。", "适合通过短视频或名片增加曝光。", "表达越具体，合作机会越稳。"]}', 'seven_kills',
  '{"trait": "果断、有魄力", "monthlyAdvice": "本月适合挑战情绪更强、更有压迫感的角色设定。"}', '#FF6B35', '落日橘',
  '适合强化镜头存在感和个人辨识度。', 7, '适合用于本月试镜节奏安排和阶段目标。',
  '午时', 'fallback', '{"source": "spec-profile-fortune-backfill", "month": "2026-04-01", "zodiac": "horse", "constellation": "leo"}',
  0, 0, NULL, NULL, 'spec-backfill', NOW(), NULL, 'spec-backfill', NOW()
)
ON DUPLICATE KEY UPDATE
  zodiac_animal=VALUES(zodiac_animal),
  zodiac_fortune=VALUES(zodiac_fortune),
  constellation=VALUES(constellation),
  constellation_fortune=VALUES(constellation_fortune),
  ziwei_star=VALUES(ziwei_star),
  ziwei_profile=VALUES(ziwei_profile),
  lucky_color=VALUES(lucky_color),
  lucky_color_name=VALUES(lucky_color_name),
  lucky_color_interpretation=VALUES(lucky_color_interpretation),
  lucky_number=VALUES(lucky_number),
  lucky_number_interpretation=VALUES(lucky_number_interpretation),
  birth_hour=VALUES(birth_hour),
  source_type=VALUES(source_type),
  raw_payload=VALUES(raw_payload),
  update_user_name='spec-backfill',
  last_update=NOW();

SELECT user_id,user_name,phone,real_auth_status,valid_invite_count FROM user WHERE user_id=10000;
SELECT actor_profile_id,user_id,nick_name,real_name,gender,age,height,location_city,avatar_url,video_url,is_certified,profile_status,birth_hour,phone,last_update FROM actor_profile WHERE user_id=10000 AND deleted=0;
SELECT experience_id,user_id,actor_profile_id,drama_name,role_name,shoot_year,shoot_month,sort_no FROM actor_experience WHERE user_id=10000 AND deleted=0 ORDER BY experience_id;
SELECT fortune_report_id,user_id,report_month,lucky_color,lucky_color_name,lucky_number,birth_hour,source_type,last_update FROM fortune_report WHERE user_id=10000 AND deleted=0 ORDER BY report_month DESC;
