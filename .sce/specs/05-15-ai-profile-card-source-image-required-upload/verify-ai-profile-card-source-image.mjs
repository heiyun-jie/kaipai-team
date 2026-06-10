import fs from 'node:fs';
import path from 'node:path';

const repoRoot = process.argv[2];
if (!repoRoot) {
  throw new Error('Usage: node verify-ai-profile-card-source-image.mjs <kaipai-frontend-root>');
}

const target = path.join(repoRoot, 'src', 'pkg-card', 'ai-profile-card', 'index.vue');
const source = fs.readFileSync(target, 'utf8');

const requiredSnippets = [
  "import { chooseImageFiles } from '@/utils/media-picker';",
  "import { uploadImage } from '@/utils/upload';",
  "import { getOptionalMyActorProfile, updateActorProfile } from '@/api/actor';",
  'analysisImageUploading',
  'analysisImageUrl',
  'profile = ref',
  'handleUploadAnalysisImage',
  'syncAnalysisImageToProfile',
  'buildAnalysisImageProfilePayload',
  'removeAnalysisImage',
  'if (!profile.value) {',
  '请先完善演员档案后再上传分析图',
  '请先上传分析图',
  '分析图上传中，请稍后',
  'sourceImageUrl: analysisImageUrl.value',
  'ai-profile-card-page__analysis-card',
  'ai-profile-card-page__analysis-empty',
  'ai-profile-card-page__analysis-preview',
];

const missing = requiredSnippets.filter((snippet) => !source.includes(snippet));

if (missing.length) {
  console.error('AI profile card source-image upload verification failed.');
  console.error('Missing snippets:');
  for (const snippet of missing) {
    console.error(`- ${snippet}`);
  }
  process.exit(1);
}

console.log('AI profile card source-image upload verification passed.');
