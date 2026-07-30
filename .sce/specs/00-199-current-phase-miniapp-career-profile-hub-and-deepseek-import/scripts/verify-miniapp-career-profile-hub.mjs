import { readFile } from 'node:fs/promises'
import { resolve } from 'node:path'
import { spawnSync } from 'node:child_process'

const repositoryRoot = resolve(import.meta.dirname, '..', '..', '..', '..')

async function readText(path) {
  try {
    return await readFile(resolve(repositoryRoot, path), 'utf8')
  } catch (error) {
    throw new Error(`Cannot read ${path}: ${error.message}`)
  }
}

function assertMatch(source, pattern, label) {
  if (!pattern.test(source)) {
    throw new Error(`${label}: expected ${pattern} to match`)
  }
}

function assertNoMatch(source, pattern, label) {
  if (pattern.test(source)) {
    throw new Error(`${label}: forbidden pattern ${pattern} matched`)
  }
}

function assertEqual(actual, expected, label) {
  if (JSON.stringify(actual) !== JSON.stringify(expected)) {
    throw new Error(`${label}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`)
  }
}

let functionScopedMutationCount = 0

function assertMutationTurnsGateRed(source, pattern, replacement, assertion, label, options = {}) {
  const { requireUnique = false, expectedFailurePattern = null } = options
  if (requireUnique) {
    const matchCount = typeof pattern === 'string'
      ? source.split(pattern).length - 1
      : [...source.matchAll(new RegExp(pattern.source, `${pattern.flags.replace(/[gy]/g, '')}g`))].length
    assertEqual(matchCount, 1, `${label} mutation target is unique`)
  }
  const mutated = source.replace(pattern, replacement)
  if (mutated === source) throw new Error(`${label}: mutation target did not match`)
  let rejected = false
  let rejection = null
  try {
    assertion(mutated, `${label} mutation`)
  } catch (error) {
    rejected = true
    rejection = error
  }
  assertEqual(rejected, true, `${label} turns the function-scoped gate RED`)
  if (expectedFailurePattern) {
    assertMatch(
      rejection instanceof Error ? rejection.message : String(rejection),
      expectedFailurePattern,
      `${label} fails for the target contract`,
    )
  }
  functionScopedMutationCount += 1
}

function extractSfcSections(source, label) {
  const templateStart = source.indexOf('<template')
  const scriptStart = source.indexOf('<script')
  if (templateStart < 0) throw new Error(`${label}: missing outer <template> block`)
  if (scriptStart < 0 || scriptStart <= templateStart) throw new Error(`${label}: missing <script> block after template`)

  const templateOpenEnd = source.indexOf('>', templateStart)
  const templateClose = source.lastIndexOf('</template>', scriptStart)
  if (templateOpenEnd < 0 || templateOpenEnd >= scriptStart || templateClose <= templateOpenEnd) {
    throw new Error(`${label}: invalid outer <template> boundaries`)
  }

  const scriptOpenEnd = source.indexOf('>', scriptStart)
  const scriptClose = source.indexOf('</script>', scriptOpenEnd + 1)
  if (scriptOpenEnd < 0 || scriptClose <= scriptOpenEnd) {
    throw new Error(`${label}: invalid <script> boundaries`)
  }

  const styleStart = source.indexOf('<style', scriptClose + '</script>'.length)
  if (styleStart < 0) throw new Error(`${label}: missing <style> block after script`)
  const styleOpenEnd = source.indexOf('>', styleStart)
  const styleClose = source.indexOf('</style>', styleOpenEnd + 1)
  if (styleOpenEnd < 0 || styleClose <= styleOpenEnd) {
    throw new Error(`${label}: invalid <style> boundaries`)
  }

  return {
    template: source.slice(templateOpenEnd + 1, templateClose),
    script: source.slice(scriptOpenEnd + 1, scriptClose),
    style: source.slice(styleOpenEnd + 1, styleClose),
  }
}

function extractFunctionBlock(source, signaturePattern, label) {
  const signatureMatch = signaturePattern.exec(source)
  if (!signatureMatch) {
    throw new Error(`${label}: expected function signature ${signaturePattern} to match`)
  }

  const openingBrace = source.indexOf('{', signatureMatch.index + signatureMatch[0].length)
  if (openingBrace < 0) throw new Error(`${label}: function has no body`)

  let depth = 1
  for (let index = openingBrace + 1; index < source.length; index += 1) {
    if (source[index] === '{') depth += 1
    if (source[index] === '}') depth -= 1
    if (depth === 0) return source.slice(openingBrace + 1, index)
  }

  throw new Error(`${label}: function body is unterminated`)
}

function assertStyleBlock(source, selectorPattern, propertyPattern, label) {
  const selectorFlags = selectorPattern.flags.replace(/[gy]/g, '')
  const exactSelectorPattern = new RegExp(
    `(?:^|(?<=[{};]))\\s*(?:${selectorPattern.source})(?=\\s*\\{)`,
    `${selectorFlags}g`,
  )
  const declarationBlocks = []
  let selectorMatch = exactSelectorPattern.exec(source)

  while (selectorMatch) {
    const openingBrace = source.indexOf('{', exactSelectorPattern.lastIndex)
    let depth = 1
    let declarations = ''
    let index = openingBrace + 1
    for (; index < source.length && depth > 0; index += 1) {
      const character = source[index]
      if (character === '{') {
        depth += 1
      } else if (character === '}') {
        depth -= 1
      } else if (depth === 1) {
        declarations += character
      }
    }

    if (depth !== 0) {
      throw new Error(`${label}: selector ${selectorPattern} has an unterminated declaration block`)
    }
    declarationBlocks.push(declarations)
    exactSelectorPattern.lastIndex = index
    selectorMatch = exactSelectorPattern.exec(source)
  }

  if (declarationBlocks.length === 0) {
    throw new Error(`${label}: expected exact selector ${selectorPattern} to match`)
  }

  const declarations = declarationBlocks.join('\n')
  const finalDeclarations = declarationBlocks[declarationBlocks.length - 1].replace(/\/\*[\s\S]*?\*\//g, '')
  const propertyFlags = propertyPattern.flags.replace(/[gy]/g, '')
  const expectedPattern = new RegExp(propertyPattern.source, `${propertyFlags}g`)
  const expectedMatches = [...finalDeclarations.matchAll(expectedPattern)]
  const matchedProperty = expectedMatches.at(-1)?.[0].match(/([a-z-]+)\s*:/i)?.[1].toLowerCase()
  let effectiveDeclaration = finalDeclarations

  if (matchedProperty) {
    const parsedDeclarations = [...finalDeclarations.matchAll(/(?:^|;)\s*([a-z-]+)\s*:\s*([^;{}]*)(?=;|$)/gi)]
    const matchingDeclarations = parsedDeclarations.filter((match) => match[1].toLowerCase() === matchedProperty)
    const finalMatch = matchingDeclarations.at(-1)
    effectiveDeclaration = finalMatch ? `\n${finalMatch[1]}: ${finalMatch[2]};` : ''
  }

  propertyPattern.lastIndex = 0
  if (expectedMatches.length === 0 || !propertyPattern.test(effectiveDeclaration)) {
    throw new Error(`${label}: expected ${propertyPattern} in the final selector ${selectorPattern} block`)
  }

  return declarations
}

const requiredWarmProfileTokens = [
  '$kp-color-bg',
  '$kp-color-card',
  '$kp-color-text-primary',
  '$kp-color-text-secondary',
  '$kp-color-text-tertiary',
  '$kp-color-divider',
  '$kp-color-border',
  '$kp-color-primary',
  '$kp-color-dark-primary',
  '$kp-color-danger',
]
const forbiddenLegacyProfilePalette = /#(?:f5f5f5|ffffff|fff|191919|242424|ededed|dedede|d9d9d9|8c8c8c|777777|777|666666|666|555555|555|f2f2f2|f0f0f0|eeeeee|eee|e5e5e5|f7f7f7|b2b2b2|576b95|7a3e3e)(?![0-9a-f])/i

function assertWarmProfileTokenContract(page, style, label) {
  for (const token of requiredWarmProfileTokens) {
    assertMatch(style, new RegExp(escapeRegExp(token)), `${label} uses shared ${token}`)
  }
  assertNoMatch(page, forbiddenLegacyProfilePalette, `${label} does not recreate the legacy cool-gray palette`)
  assertNoMatch(style, /\$kp-font-family-display/, `${label} keeps compact operational typography`)
}

function assertNeutralProfilePackageShell(page, sections, pageClass, label, contract = {}) {
  const {
    groupSelectors = [],
    primaryActionSelectors = [],
    buttonSelectors = [],
  } = contract
  const renderedTemplate = sections.template.replace(/<!--[\s\S]*?-->/g, '')
  assertMatch(renderedTemplate, /<KpFloatingBackButton\b[^>]*\/?\s*>/, `${label} renders the shared floating back button`)
  assertMatch(sections.template, new RegExp(`${pageClass}__nav`), `${label} has a neutral navigation shell`)
  const pageSelector = new RegExp(`\\.${pageClass}(?=\\s*\\{)`)
  const navSelector = new RegExp(`[^{}]*\\.${pageClass}__nav(?![\\w-])[^{}]*`)
  const navTitleSelector = new RegExp(`\\.${pageClass}__nav-title(?=\\s*\\{)`)
  assertStyleBlock(
    sections.style,
    pageSelector,
    /background:\s*(?:\$kp-color-bg|linear-gradient\([^;{}]*\$kp-color-bg[^;{}]*\))\s*;/i,
    `${label} shared warm page background`,
  )
  assertStyleBlock(sections.style, pageSelector, /color:\s*\$kp-color-text-primary\s*;/i, `${label} primary text token`)
  assertStyleBlock(sections.style, navSelector, /position:\s*sticky\s*;/i, `${label} sticky navigation`)
  assertStyleBlock(sections.style, navSelector, /top:\s*0\s*;/i, `${label} navigation stays at the viewport top`)
  assertStyleBlock(sections.style, navSelector, /z-index:\s*30\s*;/i, `${label} navigation stays above page content`)
  assertStyleBlock(sections.style, navSelector, /background:\s*\$kp-color-card\s*;/i, `${label} shared warm navigation surface`)
  assertStyleBlock(sections.style, navTitleSelector, /color:\s*\$kp-color-text-primary\s*;/i, `${label} shared navigation title`)
  assertStyleBlock(sections.style, navTitleSelector, /font-size:\s*32rpx\s*;/i, `${label} compact navigation title`)
  assertStyleBlock(sections.style, navTitleSelector, /(?:justify-content|text-align):\s*center\s*;/i, `${label} centered navigation title`)
  assertMatch(sections.style, /\$kp-color-divider/, `${label} shared dividers`)
  assertMatch(sections.style, /\$kp-color-border/, `${label} shared borders`)
  assertMatch(sections.style, /\$kp-color-primary/, `${label} shared accent`)
  for (const selector of groupSelectors) {
    const declarations = assertStyleBlock(sections.style, selector, /background:\s*\$kp-color-card\s*;/i, `${label} shared warm content group`)
    assertNoMatch(declarations, /border-radius|box-shadow/i, `${label} content groups stay square and flat`)
  }
  for (const selector of primaryActionSelectors) {
    assertStyleBlock(sections.style, selector, /background:\s*\$kp-color-dark-primary\s*;/i, `${label} shared dark primary action`)
    assertStyleBlock(
      sections.style,
      selector,
      /color:\s*(?:\$kp-color-text-dark-primary|\$kp-color-card)\s*;/i,
      `${label} primary action uses a shared light text token`,
    )
  }
  for (const selector of buttonSelectors) {
    assertStyleBlock(sections.style, selector, /border-radius:\s*(?:12|14|16)rpx\s*;/i, `${label} command button uses a 6-8px radius`)
  }
  assertWarmProfileTokenContract(page, sections.style, label)
}

const profileArtifactRoutes = [
  'import-review/index',
  'works/index',
  'work-edit/index',
  'assets/index',
]
const profileArtifactPages = [
  { path: 'import-review', rootClass: 'import-review' },
  { path: 'works', rootClass: 'works-page' },
  { path: 'work-edit', rootClass: 'work-edit' },
  { path: 'assets', rootClass: 'assets-page' },
]
const profileArtifactExtensions = ['js', 'json', 'wxml', 'wxss']
const requiredCompiledWarmProfilePalette = [
  /#f5f3ee/i,
  /#fbfaf6/i,
  /#1a1816/i,
  /rgba\(26\s*,\s*24\s*,\s*22\s*,\s*0?\.52\)/i,
  /rgba\(26\s*,\s*24\s*,\s*22\s*,\s*0?\.38\)/i,
  /rgba\(26\s*,\s*24\s*,\s*22\s*,\s*0?\.08\)/i,
  /rgba\(26\s*,\s*24\s*,\s*22\s*,\s*0?\.1\)/i,
  /#8c6f4f/i,
  /#1d1814/i,
  /#8b6258/i,
]

function parseJson(source, label) {
  try {
    return JSON.parse(source)
  } catch (error) {
    throw new Error(`${label}: invalid JSON: ${error.message}`)
  }
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function assertCompiledAppContract(source, label) {
  const app = parseJson(source, label)
  const profilePackages = Array.isArray(app.subPackages)
    ? app.subPackages.filter((item) => item?.root === 'pkg-profile')
    : []
  assertEqual(profilePackages.length, 1, `${label} pkg-profile registration count`)
  assertEqual(profilePackages[0]?.pages, profileArtifactRoutes, `${label} pkg-profile routes`)
}

function assertCompiledPageJsonContract(source, label) {
  const page = parseJson(source, label)
  assertEqual(page.backgroundColor, '#F5F3EE', `${label} shared warm backgroundColor`)
  assertEqual(page.navigationStyle, 'custom', `${label} navigationStyle`)
  assertEqual(
    page.usingComponents?.['kp-floating-back-button'],
    '../../components/KpFloatingBackButton',
    `${label} component registration`,
  )
}

function parseCompiledWxmlAttributes(attributes, tagName, label) {
  let cursor = 0
  let classValue = null
  let hasClassAttribute = false

  while (cursor < attributes.length) {
    while (/\s/.test(attributes[cursor] || '')) cursor += 1
    if (cursor >= attributes.length) break
    if (attributes[cursor] === '/') {
      cursor += 1
      continue
    }

    const nameStart = cursor
    while (/[A-Za-z0-9_:@.\-]/.test(attributes[cursor] || '')) cursor += 1
    if (cursor === nameStart) {
      throw new Error(`${label}: invalid attribute syntax in <${tagName}>`)
    }
    const attributeName = attributes.slice(nameStart, cursor)
    while (/\s/.test(attributes[cursor] || '')) cursor += 1

    let attributeValue = null
    if (attributes[cursor] === '=') {
      cursor += 1
      while (/\s/.test(attributes[cursor] || '')) cursor += 1
      const quote = attributes[cursor]
      if (quote !== '"' && quote !== "'") {
        throw new Error(`${label}: ${attributeName} in <${tagName}> must use a quoted value`)
      }
      cursor += 1
      const valueStart = cursor
      while (cursor < attributes.length && attributes[cursor] !== quote) cursor += 1
      if (cursor >= attributes.length) {
        throw new Error(`${label}: unterminated ${attributeName} value in <${tagName}>`)
      }
      attributeValue = attributes.slice(valueStart, cursor)
      cursor += 1
    }

    if (attributeName === 'class') {
      if (hasClassAttribute) throw new Error(`${label}: duplicate class attribute in <${tagName}>`)
      if (attributeValue === null) throw new Error(`${label}: class in <${tagName}> must use a quoted value`)
      hasClassAttribute = true
      classValue = attributeValue
    }
  }

  return classValue
}

function extractCompiledWxmlElements(source, label) {
  const renderedSource = source.replace(/<!--[\s\S]*?-->/g, '')
  const elements = []

  for (let index = 0; index < renderedSource.length; index += 1) {
    if (renderedSource[index] !== '<' || !/[A-Za-z]/.test(renderedSource[index + 1] || '')) continue

    let cursor = index + 1
    while (/[A-Za-z0-9_:-]/.test(renderedSource[cursor] || '')) cursor += 1
    const tagName = renderedSource.slice(index + 1, cursor).toLowerCase()
    const attributesStart = cursor
    let quote = null
    for (; cursor < renderedSource.length; cursor += 1) {
      const character = renderedSource[cursor]
      if (quote) {
        if (character === quote) quote = null
      } else if (character === '"' || character === "'") {
        quote = character
      } else if (character === '>') {
        break
      }
    }
    if (cursor >= renderedSource.length) throw new Error(`${label}: unterminated <${tagName}> tag`)

    const attributes = renderedSource.slice(attributesStart, cursor)
    elements.push({
      tagName,
      classValue: parseCompiledWxmlAttributes(attributes, tagName, label),
    })
    index = cursor
  }

  return elements
}

function hasCompiledClassToken(classValue, classToken) {
  return new RegExp(`(?:^|[^A-Za-z0-9_-])${escapeRegExp(classToken)}(?![A-Za-z0-9_-])`).test(classValue)
}

function requireCompiledClassElement(elements, classToken, label) {
  const matches = elements.filter((element) => (
    element.classValue !== null && hasCompiledClassToken(element.classValue, classToken)
  ))
  assertEqual(matches.length, 1, label)
  return matches[0]
}

function requireCompiledScopeToken(element, label) {
  if (element.classValue === null) throw new Error(`${label}: missing parseable class attribute`)
  const scopes = [...element.classValue.matchAll(/(?:^|[^A-Za-z0-9_-])(data-v-[A-Za-z0-9_-]+)(?![A-Za-z0-9_-])/g)]
    .map((match) => match[1])
  assertEqual(scopes.length, 1, `${label} scope count`)
  return scopes[0]
}

function assertCompiledWxmlContract(source, rootClass, label) {
  const elements = extractCompiledWxmlElements(source, label)
  const root = requireCompiledClassElement(elements, rootClass, `${label} root class match count`)
  const navigation = requireCompiledClassElement(elements, `${rootClass}__nav`, `${label} navigation class match count`)
  const navigationTitle = requireCompiledClassElement(elements, `${rootClass}__nav-title`, `${label} navigation title class match count`)
  const backButtons = elements.filter((element) => element.tagName === 'kp-floating-back-button')
  assertEqual(backButtons.length, 1, `${label} shared floating back button count`)

  const scopes = [
    requireCompiledScopeToken(root, `${label} root class`),
    requireCompiledScopeToken(navigation, `${label} navigation class`),
    requireCompiledScopeToken(navigationTitle, `${label} navigation title class`),
    requireCompiledScopeToken(backButtons[0], `${label} shared floating back button class`),
  ]
  assertEqual([...new Set(scopes)].length, 1, `${label} shared scope token`)
  return scopes[0]
}

function compiledClassSelector(className, scopeToken) {
  return new RegExp(`\\.${escapeRegExp(className)}\\.${escapeRegExp(scopeToken)}`)
}

function extractCompiledStyleRules(source, label) {
  const renderedSource = source.replace(/\/\*[\s\S]*?\*\//g, '')
  const rules = []
  let cursor = 0

  while (cursor < renderedSource.length) {
    while (/\s/.test(renderedSource[cursor] || '')) cursor += 1
    if (cursor >= renderedSource.length) break

    const openingBrace = renderedSource.indexOf('{', cursor)
    if (openingBrace < 0) throw new Error(`${label}: trailing CSS without a declaration block`)
    const selectorSource = renderedSource.slice(cursor, openingBrace).trim()
    if (!selectorSource) throw new Error(`${label}: CSS rule has no selector`)

    let depth = 1
    let quote = null
    let closingBrace = openingBrace + 1
    for (; closingBrace < renderedSource.length && depth > 0; closingBrace += 1) {
      const character = renderedSource[closingBrace]
      if (quote) {
        if (character === '\\') {
          closingBrace += 1
        } else if (character === quote) {
          quote = null
        }
      } else if (character === '"' || character === "'") {
        quote = character
      } else if (character === '{') {
        throw new Error(`${label}: nested compiled CSS rules are unsupported`)
      } else if (character === '}') {
        depth -= 1
      }
    }
    if (depth !== 0) throw new Error(`${label}: CSS rule is unterminated`)

    rules.push({
      selectors: selectorSource.split(',').map((selector) => selector.trim()),
      declarations: renderedSource.slice(openingBrace + 1, closingBrace - 1),
    })
    cursor = closingBrace
  }

  return rules
}

function selectorHasExactClassToken(selector, classToken) {
  return new RegExp(`\\.${escapeRegExp(classToken)}(?![A-Za-z0-9_-])`).test(selector)
}

function assertNoConflictingCompiledDeclarations(rules, classToken, expectedValues, label) {
  const matchingRules = rules.filter((rule) => (
    rule.selectors.some((selector) => selectorHasExactClassToken(selector, classToken))
  ))

  for (const rule of matchingRules) {
    const declarations = [...rule.declarations.matchAll(/(?:^|;)\s*([a-z-]+)\s*:\s*([^;{}]*)(?=;|$)/gi)]
    for (const declaration of declarations) {
      const property = declaration[1].toLowerCase()
      if (!Object.prototype.hasOwnProperty.call(expectedValues, property)) continue
      const value = declaration[2].trim().toLowerCase()
      if (/!important\b/i.test(value)) {
        throw new Error(`${label} conflicting ${property}: !important is forbidden`)
      }
      if (value !== expectedValues[property]) {
        throw new Error(`${label} conflicting ${property}: expected ${expectedValues[property]}, got ${value}`)
      }
    }
  }
}

function assertCompiledWxssContract(source, rootClass, scopeToken, label) {
  assertMatch(scopeToken, /^data-v-[A-Za-z0-9_-]+$/, `${label} WXML scope token`)
  const rootSelector = compiledClassSelector(rootClass, scopeToken)
  const navSelector = compiledClassSelector(`${rootClass}__nav`, scopeToken)
  const navTitleSelector = compiledClassSelector(`${rootClass}__nav-title`, scopeToken)
  assertStyleBlock(
    source,
    rootSelector,
    /background(?:-color)?:\s*(?:#f5f3ee|linear-gradient\([^;{}]*#f5f3ee[^;{}]*\))(?:\s*;|$)/i,
    `${label} root scoped selector shared warm background`,
  )
  assertStyleBlock(source, rootSelector, /color:\s*#1a1816(?:\s*;|$)/i, `${label} root scoped selector text`)
  assertStyleBlock(source, navSelector, /position:\s*sticky(?:\s*;|$)/i, `${label} navigation scoped selector position`)
  assertStyleBlock(source, navSelector, /top:\s*0(?:\s*;|$)/i, `${label} navigation scoped selector top`)
  assertStyleBlock(source, navSelector, /z-index:\s*30(?:\s*;|$)/i, `${label} navigation scoped selector layer`)
  assertStyleBlock(source, navSelector, /background(?:-color)?:\s*#fbfaf6(?:\s*;|$)/i, `${label} navigation scoped selector background`)
  assertStyleBlock(source, navTitleSelector, /color:\s*#1a1816(?:\s*;|$)/i, `${label} navigation title scoped selector text`)
  assertStyleBlock(source, navTitleSelector, /font-size:\s*32rpx(?:\s*;|$)/i, `${label} navigation title scoped selector size`)

  const rules = extractCompiledStyleRules(source, label)
  assertNoConflictingCompiledDeclarations(rules, rootClass, {
    color: '#1a1816',
  }, `${label}`)
  assertNoConflictingCompiledDeclarations(rules, `${rootClass}__nav`, {
    position: 'sticky',
    top: '0',
    'z-index': '30',
    background: '#fbfaf6',
    'background-color': '#fbfaf6',
  }, `${label}`)
  assertNoConflictingCompiledDeclarations(rules, `${rootClass}__nav-title`, {
    color: '#1a1816',
    'font-size': '32rpx',
  }, `${label}`)
  for (const value of requiredCompiledWarmProfilePalette) {
    assertMatch(source, value, `${label} emits the shared warm palette`)
  }
  assertNoMatch(source, forbiddenLegacyProfilePalette, `${label} excludes the legacy cool-gray palette`)
}

function assertSameText(actual, expected, label) {
  if (actual !== expected) throw new Error(`${label}: build/dev content differs`)
}

async function verifyBuiltArtifacts() {
  const artifactDirectories = [
    { label: 'Build', path: 'kaipai-frontend/dist/build/mp-weixin' },
    { label: 'Dev', path: 'kaipai-frontend/dist/dev/mp-weixin' },
  ]
  const pageArtifactPaths = profileArtifactPages.flatMap(({ path }) => (
    profileArtifactExtensions.map((extension) => `pkg-profile/${path}/index.${extension}`)
  ))
  const artifacts = await Promise.all(artifactDirectories.map(async (directory) => {
    const [appJson, pageFiles] = await Promise.all([
      readText(`${directory.path}/app.json`),
      Promise.all(pageArtifactPaths.map(async (path) => [path, await readText(`${directory.path}/${path}`)])),
    ])
    return {
      ...directory,
      appJson,
      pageFiles: new Map(pageFiles),
    }
  }))
  const [buildArtifacts, devArtifacts] = artifacts

  assertCompiledAppContract(buildArtifacts.appJson, 'Build app.json')
  assertCompiledAppContract(devArtifacts.appJson, 'Dev app.json')

  for (const { path, rootClass } of profileArtifactPages) {
    for (const artifactsForDirectory of artifacts) {
      const pageLabel = `${artifactsForDirectory.label} ${path}`
      assertCompiledPageJsonContract(artifactsForDirectory.pageFiles.get(`pkg-profile/${path}/index.json`), `${pageLabel} JSON`)
      const scopeToken = assertCompiledWxmlContract(artifactsForDirectory.pageFiles.get(`pkg-profile/${path}/index.wxml`), rootClass, `${pageLabel} WXML`)
      assertCompiledWxssContract(artifactsForDirectory.pageFiles.get(`pkg-profile/${path}/index.wxss`), rootClass, scopeToken, `${pageLabel} WXSS`)
    }
  }

  for (const path of pageArtifactPaths) {
    assertSameText(
      buildArtifacts.pageFiles.get(path),
      devArtifacts.pageFiles.get(path),
      `${path} synchronization`,
    )
  }

  const artifactMutationStartCount = functionScopedMutationCount
  assertMutationTurnsGateRed(
    buildArtifacts.appJson,
    '"assets/index"',
    '"assets-missing/index"',
    (source) => assertCompiledAppContract(source, 'Build app.json'),
    'build app route removal',
    { requireUnique: true, expectedFailurePattern: /Build app\.json pkg-profile routes/ },
  )
  assertMutationTurnsGateRed(
    devArtifacts.appJson,
    '"assets/index"',
    '"assets-missing/index"',
    (source) => assertCompiledAppContract(source, 'Dev app.json'),
    'dev app route removal',
    { requireUnique: true, expectedFailurePattern: /Dev app\.json pkg-profile routes/ },
  )
  assertMutationTurnsGateRed(
    buildArtifacts.pageFiles.get('pkg-profile/import-review/index.json'),
    '"../../components/KpFloatingBackButton"',
    '"../../components/DeadFloatingBackButton"',
    (source) => assertCompiledPageJsonContract(source, 'Build import-review JSON'),
    'build page JSON back-button registration replacement',
    { requireUnique: true, expectedFailurePattern: /Build import-review JSON component registration/ },
  )
  assertMutationTurnsGateRed(
    buildArtifacts.pageFiles.get('pkg-profile/import-review/index.wxml'),
    /<kp-floating-back-button\b[^>]*\/>/,
    '',
    (source) => assertCompiledWxmlContract(source, 'import-review', 'Build import-review WXML'),
    'build WXML back-button removal',
    { requireUnique: true, expectedFailurePattern: /Build import-review WXML shared floating back button/ },
  )
  assertMutationTurnsGateRed(
    buildArtifacts.pageFiles.get('pkg-profile/import-review/index.wxml'),
    /class="import-review (data-v-[\w-]+)">/,
    'class="$1"><text class="$1">import-review</text>',
    (source) => assertCompiledWxmlContract(source, 'import-review', 'Build import-review WXML'),
    'build WXML root-class text decoy',
    { requireUnique: true, expectedFailurePattern: /Build import-review WXML root class/ },
  )
  assertMutationTurnsGateRed(
    buildArtifacts.pageFiles.get('pkg-profile/import-review/index.wxml'),
    /class="import-review__nav (data-v-[\w-]+)"/,
    'class="$1" data-contract="import-review__nav"',
    (source) => assertCompiledWxmlContract(source, 'import-review', 'Build import-review WXML'),
    'build WXML navigation-class data-contract decoy',
    { requireUnique: true, expectedFailurePattern: /Build import-review WXML navigation class/ },
  )
  assertMutationTurnsGateRed(
    buildArtifacts.pageFiles.get('pkg-profile/import-review/index.wxml'),
    /<kp-floating-back-button\b[^>]*\/>/,
    '<!--$&-->',
    (source) => assertCompiledWxmlContract(source, 'import-review', 'Build import-review WXML'),
    'build WXML commented back-button decoy',
    { requireUnique: true, expectedFailurePattern: /Build import-review WXML shared floating back button/ },
  )
  assertMutationTurnsGateRed(
    buildArtifacts.pageFiles.get('pkg-profile/import-review/index.wxml'),
    /class="([^"]*)"/g,
    'data-contract=" class=\'$1\'"',
    (source) => assertCompiledWxmlContract(source, 'import-review', 'Build import-review WXML'),
    'build WXML embedded fake-class attributes',
    { expectedFailurePattern: /Build import-review WXML root class/ },
  )
  const devAssetsWxml = devArtifacts.pageFiles.get('pkg-profile/assets/index.wxml')
  const devAssetsWxss = devArtifacts.pageFiles.get('pkg-profile/assets/index.wxss')
  const devAssetsScope = assertCompiledWxmlContract(devAssetsWxml, 'assets-page', 'Dev assets WXML')
  assertMutationTurnsGateRed(
    devAssetsWxss,
    /(\.assets-page__nav(?:\.data-v-[\w-]+)?\{[^{}]*\bposition:)sticky(;)/i,
    '$1relative$2',
    (source) => assertCompiledWxssContract(source, 'assets-page', devAssetsScope, 'Dev assets WXSS'),
    'dev WXSS sticky-navigation regression',
    { requireUnique: true, expectedFailurePattern: /Dev assets WXSS navigation scoped selector position/ },
  )
  assertMutationTurnsGateRed(
    devAssetsWxss,
    /$/,
    `.assets-page.${devAssetsScope} .assets-page__nav.${devAssetsScope}{position:relative!important;top:auto!important;z-index:99!important}`,
    (source) => assertCompiledWxssContract(source, 'assets-page', devAssetsScope, 'Dev assets WXSS'),
    'dev WXSS high-specificity navigation override',
    { requireUnique: true, expectedFailurePattern: /Dev assets WXSS conflicting position/ },
  )
  assertMutationTurnsGateRed(
    devAssetsWxml,
    /data-v-[A-Za-z0-9_-]+/g,
    'data-v-deadbeef',
    (source) => {
      const mutatedScope = assertCompiledWxmlContract(source, 'assets-page', 'Dev assets WXML')
      assertCompiledWxssContract(devAssetsWxss, 'assets-page', mutatedScope, 'Dev assets WXSS')
    },
    'dev WXML and WXSS scope mismatch',
    { expectedFailurePattern: /Dev assets WXSS root scoped selector/ },
  )

  return {
    synchronizedArtifactCount: pageArtifactPaths.length,
    artifactMutationCount: functionScopedMutationCount - artifactMutationStartCount,
  }
}

function runAuthoritativePackageAudit() {
  const frontendRoot = resolve(repositoryRoot, 'kaipai-frontend')
  const buildDirectory = resolve(frontendRoot, 'dist', 'build', 'mp-weixin')
  const auditScript = resolve(frontendRoot, 'scripts', 'audit-mp-package.ps1')
  const audit = spawnSync(
    'powershell.exe',
    ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', auditScript, '-BuildDir', buildDirectory, '-LimitMB', '2'],
    { cwd: frontendRoot, stdio: 'inherit', windowsHide: true },
  )

  if (audit.error) throw new Error(`Authoritative package audit could not start: ${audit.error.message}`)
  if (audit.signal) throw new Error(`Authoritative package audit terminated by signal ${audit.signal}`)
  if (audit.status === null) throw new Error('Authoritative package audit terminated without an exit status')
  if (audit.status !== 0) throw new Error(`Authoritative package audit failed with exit code ${audit.status}`)
}

const verifierArguments = process.argv.slice(2)
if (verifierArguments.length > 1 || (verifierArguments.length === 1 && verifierArguments[0] !== '--source-only')) {
  throw new Error(`Unsupported verifier arguments: ${verifierArguments.join(' ')}`)
}
const sourceOnly = verifierArguments[0] === '--source-only'

const pages = JSON.parse(await readText('kaipai-frontend/src/pages.json'))
const profilePackage = pages.subPackages?.find((item) => item.root === 'pkg-profile')
assertEqual(
  profilePackage?.pages?.map((item) => item.path),
  ['import-review/index', 'works/index', 'work-edit/index', 'assets/index'],
  'Profile subpackage routes',
)
for (const page of profilePackage?.pages || []) {
  assertEqual(
    page.style?.backgroundColor,
    '#F5F3EE',
    `Profile subpackage ${page.path} native background`,
  )
}
const toolsPackage = pages.subPackages?.find((item) => item.root === 'pkg-tools')
assertMatch(JSON.stringify(toolsPackage), /settings\/index/, 'Settings route')

const importStore = await readText('kaipai-frontend/src/stores/profile-import.ts')
assertMatch(importStore, /setRawText[\s\S]*rawText\.value/, 'In-memory profile import source')
assertMatch(importStore, /function clear\(\)[\s\S]*rawText\.value = ''/, 'Profile import cleanup')
assertMatch(importStore, /markApplied[\s\S]*consumeApplied/, 'One-shot profile import applied signal')
const clearExtractionDraftBody = extractFunctionBlock(
  importStore,
  /function\s+clearExtractionDraft\s*\(\s*\)\s*:\s*void/,
  'clearExtractionDraft',
)
assertMatch(clearExtractionDraftBody, /extraction\.value\s*=\s*null/, 'Extraction-only draft cleanup')
assertNoMatch(
  clearExtractionDraftBody,
  /rawText|scene|profileVersion|workLibraryVersion/,
  'Extraction cleanup preserves source scene and versions',
)
assertMatch(
  importStore,
  /function setExtraction[\s\S]*profileVersion\.value\s*=\s*value\.profileVersion[\s\S]*workLibraryVersion\.value\s*=\s*value\.workLibraryVersion/,
  'Extraction server context snapshot',
)
assertMatch(
  importStore,
  /const\s+avatarAssetId\s*=\s*ref<number\s*\|\s*null\s*\|\s*undefined>\(undefined\)/,
  'Optional profile import avatar context',
)
const setImportContextBody = extractFunctionBlock(
  importStore,
  /function\s+setContext\s*\(\s*nextScene:\s*ProfileImportScene\s*,\s*nextProfileVersion:\s*number\s*,\s*nextWorkLibraryVersion:\s*number\s*,\s*nextAvatarAssetId\?:\s*number\s*\|\s*null\s*,?\s*\)\s*:\s*void/,
  'setContext',
)
assertMatch(
  setImportContextBody,
  /avatarAssetId\.value\s*=\s*nextScene\s*===\s*'full_profile'\s*\?\s*nextAvatarAssetId\s*:\s*undefined/,
  'Works-only import cannot retain an avatar context',
)
const clearImportStoreBody = extractFunctionBlock(
  importStore,
  /function\s+clear\s*\(\s*\)\s*:\s*void/,
  'profile import clear',
)
assertMatch(clearImportStoreBody, /avatarAssetId\.value\s*=\s*undefined/, 'Profile import clear removes avatar context')
assertNoMatch(importStore, /uni\.setStorage|localStorage|persist/, 'No persisted profile import source')

const importTypes = await readText('kaipai-frontend/src/types/profile-import.ts')
const importCapabilityBody = extractFunctionBlock(
  importTypes,
  /export\s+interface\s+ProfileImportCapability/,
  'ProfileImportCapability',
)
for (const field of [
  'enabled',
  'available',
  'providerCode',
  'modelName',
  'maxInputLength',
  'unavailableReason',
]) {
  assertMatch(importCapabilityBody, new RegExp(`\\b${field}:`), `Required capability field ${field}`)
}
assertNoMatch(importCapabilityBody, /\breason\??:/, 'No legacy capability reason field')
for (const field of [
  'profileVersion',
  'workLibraryVersion',
  'confidence',
  'sourceText',
  'warning',
  'reviewStatus',
  'conflict',
  'matchStatus',
  'selectedAction',
  'matchedExperienceId',
  'allowedActions',
  'conflictFields',
  'fields',
  'conflicts',
  'confirmedConflictFields',
  'candidateValue',
]) {
  assertMatch(importTypes, new RegExp(`\\b${field}\\??:`), `Profile import contract field ${field}`)
}

const importPayloadBuilder = await readText('kaipai-frontend/src/utils/profile-import-payload.ts')
assertMatch(importPayloadBuilder, /buildProfileImportApplyRequest/, 'Pure profile import apply builder')
assertMatch(
  importPayloadBuilder,
  /candidateValue:\s*candidate\.candidateValue[\s\S]*value:\s*profileFinalValues\[candidate\.candidateId\]/,
  'Signed profile candidate value and independent final value',
)
for (const field of [
  'matchStatus',
  'selectedAction',
  'matchedExperienceId',
  'allowedActions',
  'conflictFields',
  'confirmedConflictFields',
  'projectName',
  'roleName',
  'publishStatus',
  'workTypeCode',
  'roleLevelCode',
  'shootYear',
  'shootMonth',
  'platform',
  'syncSoundStatus',
  'collaborators',
  'achievementText',
  'description',
]) {
  assertMatch(importPayloadBuilder, new RegExp(`\\b${field}:`), `Profile import apply work field ${field}`)
}
assertMatch(
  importPayloadBuilder,
  /selectedAction\s*===\s*'merge'[\s\S]*finalFields/,
  'Merge-only final work fields',
)
assertMatch(
  importPayloadBuilder,
  /scene\s*===\s*'works_only'\s*\?\s*\[\]/,
  'Works-only apply strips profile candidates',
)

const navigationStore = await readText('kaipai-frontend/src/stores/record-navigation.ts')
assertMatch(navigationStore, /openFavorites[\s\S]*'favorites'/, 'Favorites navigation intent')
assertMatch(navigationStore, /consumeSegment[\s\S]*\.value = null/, 'One-shot navigation intent')

const request = await readText('kaipai-frontend/src/utils/request.ts')
assertMatch(request, /class ApiError extends Error/, 'Structured API error class')
assertMatch(
  request,
  /new ApiError\(response\.message \|\| '请求失败', response\.code, response\.errorCode\)/,
  'Structured API error construction',
)

const profileImportApi = await readText('kaipai-frontend/src/api/profile-import.ts')
for (const [signature, requestPattern, label] of [
  [
    /export\s+function\s+getProfileImportCapability\s*\(\s*\)\s*:\s*Promise<ProfileImportCapability>/,
    /get\(\s*'\/api\/ai\/profile-import\/capability'\s*,\s*undefined\s*,\s*\{\s*showError:\s*false\s*\}\s*\)/,
    'Capability request',
  ],
  [
    /export\s+function\s+extractProfileImport\s*\([^)]*\)\s*:\s*Promise<ProfileImportExtraction>/,
    /post\(\s*'\/api\/ai\/profile-import\/extract'\s*,[\s\S]*?\{\s*showError:\s*false\s*\}\s*,?\s*\)/,
    'Extract request',
  ],
  [
    /export\s+function\s+applyProfileImport\s*\([^)]*\)\s*:\s*Promise<ProfileImportApplyResult>/,
    /post\(\s*'\/api\/actor\/profile-import\/apply'\s*,[\s\S]*?\{\s*showError:\s*false\s*\}\s*,?\s*\)/,
    'Apply request',
  ],
]) {
  const body = extractFunctionBlock(profileImportApi, signature, label)
  assertMatch(
    body,
    requestPattern,
    `${label} delegates error feedback to the page`,
  )
}

const mpSync = await readText('kaipai-frontend/scripts/sync-mp-weixin.ps1')
assertMatch(mpSync, /Apply-LocalDevProjectConfig/, 'Local MiniProgram project config sync')
assertMatch(mpSync, /\.env\.local[\s\S]*VITE_API_BASE_URL/, 'Local API override detection')
assertMatch(mpSync, /urlCheck\s*=\s*\$false/, 'Local URL validation override')

const actorApi = await readText('kaipai-frontend/src/api/actor.ts')
const profileTypes = await readText('kaipai-frontend/src/types/profile.ts')
const actorProfileRespBody = extractFunctionBlock(
  profileTypes,
  /export\s+interface\s+ActorProfileResp/,
  'ActorProfileResp',
)
for (const [field, type] of [
  ['actorProfileId', 'number'],
  ['publicName', 'string'],
  ['gender', 'ActorGender'],
  ['age', 'number'],
  ['height', 'number'],
  ['currentCity', 'string'],
  ['originPlace', 'string'],
  ['schoolName', 'string'],
  ['majorName', 'string'],
  ['intro', 'string'],
]) {
  assertMatch(
    actorProfileRespBody,
    new RegExp(`\\b${field}: ${type} \\| null;`),
    `ActorProfileResp ${field} empty-draft nullability`,
  )
}
for (const [field, typePattern] of [
  ['userId', 'number'],
  ['profileVersion', 'number'],
  ['workLibraryVersion', 'number'],
  ['languageTags', 'string\\[\\]'],
  ['specialtyTags', 'string\\[\\]'],
  ['roleTypeTags', 'string\\[\\]'],
  ['professionalAbilityTags', 'string\\[\\]'],
]) {
  assertMatch(
    actorProfileRespBody,
    new RegExp(`\\b${field}: ${typePattern};`),
    `ActorProfileResp ${field} remains required`,
  )
}
const getMyActorProfileBody = extractFunctionBlock(
  actorApi,
  /export\s+function\s+getMyActorProfile\s*\([^)]*\)\s*:\s*Promise<ActorProfile>/,
  'getMyActorProfile',
)
const getMyCareerProfileBody = extractFunctionBlock(
  actorApi,
  /export\s+function\s+getMyCareerProfile\s*\([^)]*\)\s*:\s*Promise<ActorProfileResp>/,
  'getMyCareerProfile',
)
assertMatch(
  getMyActorProfileBody,
  /get<ActorProfile>\('\/api\/actor\/profile\/mine\/legacy'/,
  'Legacy aggregate profile API route',
)
assertMatch(
  getMyCareerProfileBody,
  /get<ActorProfileResp>\('\/api\/actor\/profile\/mine'/,
  'Versioned career profile API route',
)
assertNoMatch(getMyCareerProfileBody, /\/mine\/career/, 'Deprecated career profile alias is not consumed')

const mine = await readText('kaipai-frontend/src/pages/mine/index.vue')
assertMatch(mine, /个人档案[\s\S]*作品库[\s\S]*素材库/, 'Mine profile hierarchy')
assertMatch(mine, /我的作品集[\s\S]*联系申请[\s\S]*设置/, 'Mine common actions')
assertMatch(mine, /title:\s*'我的作品集'[\s\S]{0,160}path:\s*'\/pkg-card\/portfolio\/index'/, 'Mine portfolio action route')
assertNoMatch(mine, /title:\s*'创建分享'/, 'Mine no longer exposes create-share action')
assertMatch(mine, /<KpMineIcon\s+:name="item\.icon"/, 'Mine entry icon component')
assertNoMatch(mine, /<text>\{\{\s*item\.icon\s*\}\}<\/text>/, 'No Mine text icon placeholders')
assertNoMatch(mine, /analytics|trendHeights|openMyQrCode|我的二维码/, 'Mine career hub')
assertNoMatch(mine, /我的数据|近 30 天|getMyShareCards\(|getShareCardHistory\(/, 'No pseudo Mine analytics')
assertMatch(
  mine,
  /linear-gradient\(180deg,\s*#f5f3ee 0%,\s*#f1ede6 100%\)/,
  'Mine warm neutral page background',
)
assertMatch(mine, /\$kp-font-family-display/, 'Mine display typography')
assertMatch(mine, /#8c6f4f|#a58c67/, 'Mine brand brown palette')
assertNoMatch(mine, /#202724|#245f4b|#e6f1ec|#eef0f8/, 'No foreign green Mine palette')
assertMatch(
  mine,
  /async function hydrateMinePage\(\)[\s\S]*if \(isVisitor\.value\)[\s\S]*getCareerHubSummary\(\)/,
  'Visitor-safe career hub hydration',
)

const mineIcon = await readText('kaipai-frontend/src/components/KpMineIcon.vue')
for (const name of ['profile', 'works', 'assets', 'share', 'contacts', 'settings']) {
  assertMatch(mineIcon, new RegExp(`'${name}'`), `Mine ${name} icon type`)
  const iconAsset = await readText(`kaipai-frontend/src/static/mine-icons/${name}.svg`)
  assertMatch(iconAsset, /<svg[\s\S]*stroke="#8c6f4f"/, `Mine ${name} icon asset`)
}

for (const path of [
  'kaipai-frontend/src/pages/history/index.vue',
  'kaipai-frontend/src/pkg-card/favorites/index.vue',
  'kaipai-frontend/src/pkg-tools/settings/index.vue',
]) {
  const page = await readText(path)
  assertMatch(page, /\$kp-color-bg|#f5f3ee/, `${path} warm page background`)
  assertMatch(page, /\$kp-color-primary|#8c6f4f/, `${path} brand brown accent`)
  assertMatch(page, /\$kp-font-family-display/, `${path} display typography`)
  assertNoMatch(
    page,
    /#f3f5f4|#202421|#245f4b|#dfe4e1|#edf0ee|#eef0f8|#44547d/,
    `${path} foreign green-gray palette`,
  )
}

const history = await readText('kaipai-frontend/src/pages/history/index.vue')
assertMatch(history, /'history'[\s\S]*'favorites'/, 'Record segments')
assertMatch(history, /getShareCardHistory[\s\S]*listShareCardFavorites/, 'Independent record sources')
const historySections = extractSfcSections(history, 'Record page SFC')
const hydrateActiveSegmentBody = extractFunctionBlock(
  historySections.script,
  /async\s+function\s+hydrateActiveSegment\s*\(\s*\)\s*:\s*Promise<void>/,
  'hydrateActiveSegment',
)
assertMatch(historySections.script, /let\s+recordRequestRevision\s*=\s*0/, 'Record request revision')
assertMatch(
  historySections.script,
  /function\s+isCurrentRecordRequest\s*\(\s*revision:\s*number,\s*segment:\s*RecordSegment\s*\)\s*:\s*boolean[\s\S]*revision\s*===\s*recordRequestRevision[\s\S]*activeSegment\.value\s*===\s*segment/,
  'Record request currentness helper',
)
assertMatch(
  hydrateActiveSegmentBody,
  /const\s+requestedSegment\s*=\s*activeSegment\.value[\s\S]*const\s+requestRevision\s*=\s*\+\+recordRequestRevision/,
  'Record request captures segment and revision',
)
assertMatch(
  hydrateActiveSegmentBody,
  /if\s*\(\s*!userStore\.hasStoredSession\s*\)\s*\{[\s\S]*loading\.value\s*=\s*false[\s\S]*return/,
  'Visitor hydration settles superseded loading state',
)
assertMatch(
  hydrateActiveSegmentBody,
  /await\s+userStore\.bootstrapSession\(\)[\s\S]*if\s*\(\s*!isCurrentRecordRequest\(requestRevision,\s*requestedSegment\)\s*\)\s*return[\s\S]*if\s*\(\s*requestedSegment\s*===\s*'history'\s*\)/,
  'Record endpoint selection uses the captured segment',
)
assertMatch(
  hydrateActiveSegmentBody,
  /const\s+nextHistoryItems\s*=\s*await\s+getShareCardHistory\(\)[\s\S]*if\s*\(\s*!isCurrentRecordRequest\(requestRevision,\s*requestedSegment\)\s*\)\s*return[\s\S]*historyItems\.value\s*=\s*nextHistoryItems/,
  'Stale history response cannot replace current data',
)
assertMatch(
  hydrateActiveSegmentBody,
  /const\s+nextFavoritePage\s*=\s*await\s+listShareCardFavorites\(1,\s*50\)[\s\S]*if\s*\(\s*!isCurrentRecordRequest\(requestRevision,\s*requestedSegment\)\s*\)\s*return[\s\S]*favoriteItems\.value\s*=\s*nextFavoritePage\.list/,
  'Stale favorite response cannot replace current data',
)
assertMatch(
  hydrateActiveSegmentBody,
  /catch\s*\(error\)\s*\{\s*if\s*\(\s*isCurrentRecordRequest\(requestRevision,\s*requestedSegment\)\s*\)\s*\{[\s\S]*loadError\.value\s*=/,
  'Stale record request cannot replace current error',
)
assertMatch(
  hydrateActiveSegmentBody,
  /finally\s*\{\s*if\s*\(\s*isCurrentRecordRequest\(requestRevision,\s*requestedSegment\)\s*\)\s*\{[\s\S]*loading\.value\s*=\s*false/,
  'Stale record request cannot clear current loading state',
)

const favorites = await readText('kaipai-frontend/src/pkg-card/favorites/index.vue')
assertMatch(favorites, /useRecordNavigationStore[\s\S]*switchTab\(\{ url: '\/pages\/history\/index' \}\)/, 'Favorite route compatibility')
assertNoMatch(favorites, /ref\(\[\]\)/, 'No fake favorite list')

const settings = await readText('kaipai-frontend/src/pkg-tools/settings/index.vue')
assertMatch(settings, /消息通知[\s\S]*偏好设置[\s\S]*用户协议[\s\S]*隐私政策[\s\S]*关于/, 'Settings hierarchy')

const actorAssetApi = await readText('kaipai-frontend/src/api/actor-asset.ts')
const actorAssetTypes = await readText('kaipai-frontend/src/types/actor-asset.ts')
assertMatch(
  actorAssetTypes,
  /ActorAssetProcessStatus\s*=\s*'uploading'\s*\|\s*'processing'\s*\|\s*'ready'\s*\|\s*'failed'/,
  'Asset process status uses uploading processing ready failed as the formal lifecycle',
)
assertMatch(actorAssetTypes, /pending[^\n]*legacy|legacy[^\n]*pending/i, 'Pending status is documented as read-only legacy compatibility')
const getActorAssetBody = extractFunctionBlock(
  actorAssetApi,
  /export\s+function\s+getActorAsset\s*\(\s*id:\s*number\s*,\s*options\?:\s*Pick<RequestOptions,\s*'showLoading'\s*\|\s*'showError'>\s*,?\s*\)\s*:\s*Promise<ActorAsset>/,
  'getActorAsset',
)
assertMatch(getActorAssetBody, /get\(\s*`\/api\/actor\/assets\/\$\{id\}`\s*,\s*undefined\s*,\s*options\s*\)/, 'Single asset polling forwards silent request options')
const retryActorPdfAssetBody = extractFunctionBlock(
  actorAssetApi,
  /export\s+function\s+retryActorPdfAsset\s*\(\s*id:\s*number\s*,\s*filePath:\s*string\s*\)\s*:\s*Promise<ActorAsset>/,
  'retryActorPdfAsset',
)
assertMatch(retryActorPdfAssetBody, /\/api\/actor\/assets\/\$\{id\}\/retry[\s\S]*filePath[\s\S]*name:\s*'file'/, 'Failed PDF retry uses the owned multipart retry endpoint')
const requestAssetAccessUrlBody = extractFunctionBlock(
  actorAssetApi,
  /export\s+function\s+requestAssetAccessUrl\s*\(\s*id:\s*number\s*,\s*options\?:\s*Pick<RequestOptions,\s*'showLoading'\s*\|\s*'showError'>\s*,?\s*\)\s*:\s*Promise<ActorAssetAccess>/,
  'requestAssetAccessUrl',
)
assertMatch(
  requestAssetAccessUrlBody,
  /post\(\s*`\/api\/actor\/assets\/\$\{id\}\/access-url`\s*,\s*undefined\s*,\s*options\s*\)/,
  'Asset access-url adapter forwards background request options',
)

const edit = await readText('kaipai-frontend/src/pages/actor-profile/edit.vue')
const { template: editTemplate, script: editScript, style: editStyle } = extractSfcSections(edit, 'Profile editor SFC')
const hydrateDraftBody = extractFunctionBlock(
  editScript,
  /function\s+hydrateDraft\s*\(\s*profile:\s*ActorProfileResp\s*\)\s*:\s*void/,
  'hydrateDraft',
)
const loadProfileBody = extractFunctionBlock(
  editScript,
  /async\s+function\s+loadProfile\s*\(\s*\)\s*:\s*Promise<void>/,
  'loadProfile',
)
const openImportReviewBody = extractFunctionBlock(
  editScript,
  /function\s+openImportReview\s*\(\s*\)\s*:\s*void/,
  'openImportReview',
)
const navigateToImportReviewBody = extractFunctionBlock(
  editScript,
  /function\s+navigateToImportReview\s*\(\s*\)\s*:\s*void/,
  'navigateToImportReview',
)
const discardNonAvatarDraftBody = extractFunctionBlock(
  editScript,
  /function\s+discardUnsavedNonAvatarChanges\s*\(\s*\)\s*:\s*void/,
  'discardUnsavedNonAvatarChanges',
)
const initialAvatarOnlyDraftBody = extractFunctionBlock(
  editScript,
  /function\s+isInitialAvatarOnlyDraft\s*\(\s*\)\s*:\s*boolean/,
  'isInitialAvatarOnlyDraft',
)
const hydrateAvatarPreviewBody = extractFunctionBlock(
  editScript,
  /async\s+function\s+hydrateAvatarPreview\s*\(\s*assetId:\s*number\s*,\s*requestRevision:\s*number\s*\)\s*:\s*Promise<void>/,
  'hydrateAvatarPreview',
)
const activeTagOptionsBody = extractFunctionBlock(
  editScript,
  /const\s+activeTagOptions\s*=\s*computed(?:\s*<[^>]+>)?\s*\(\s*\(\)\s*=>/,
  'activeTagOptions',
)
const openTagSheetBody = extractFunctionBlock(
  editScript,
  /function\s+openTagSheet\s*\(\s*key:\s*TagKey\s*\)\s*:\s*void/,
  'openTagSheet',
)
const onShowBody = extractFunctionBlock(
  editScript,
  /onShow\(\s*\(\)\s*=>/,
  'profile editor onShow',
)

assertMatch(
  editTemplate,
  /<KpFloatingBackButton\b(?=[^>]*@click="requestLeave")[^>]*>/,
  'Shared floating back button',
)
assertNoMatch(edit, /KpCapsuleSpacer|profile-edit__back|<text>‹<\/text>/, 'No private profile back control')
assertMatch(editTemplate, /从复制内容智能填写[\s\S]*核心资料/, 'Import entry precedes core profile')
assertMatch(
  editTemplate,
  /<view\b(?=[^>]*class="profile-edit__cell profile-edit__cell--action")(?=[^>]*@click="openImportReview")[^>]*>/,
  'Import cell action',
)
assertMatch(editTemplate, /class="profile-edit__cell-group"/, 'WeUI cell groups')
assertMatch(editTemplate, /v-if="careerExpanded"/, 'Inline career editor')
assertMatch(editTemplate, /v-if="introExpanded"/, 'Inline intro editor')
assertMatch(editScript, /const\s+careerExpanded\s*=\s*ref\(false\)/, 'Independent career expansion state')
assertMatch(editScript, /const\s+introExpanded\s*=\s*ref\(false\)/, 'Independent intro expansion state')
assertMatch(
  editTemplate,
  /<button\b(?=[^>]*class="profile-edit__save")(?=[^>]*:disabled="saving \|\| loading \|\| !!loadError")[^>]*>/,
  'Profile save disabled after load failure',
)
assertStyleBlock(
  editStyle,
  /&__nav\s*(?=\{)/,
  /border-bottom:\s*1rpx\s+solid\s+\$kp-color-divider\s*;/i,
  'Profile nav divider',
)
assertStyleBlock(editStyle, /&__nav-title\s*(?=\{)/, /height:\s*64rpx\s*;/, 'Profile nav capsule alignment')
assertMatch(editTemplate, /v-if="activeTagField"/, 'Tag sheet visibility state')
assertMatch(editTemplate, /class="profile-edit__tag-sheet"/, 'Bottom multi-select tag sheet')
assertMatch(editScript, /const\s+activeTagField\s*=\s*ref<TagKey\s*\|\s*null>\(null\)/, 'Shared tag field state')
assertMatch(
  editTemplate,
  /<view\b(?=[^>]*class="profile-edit__tag-row")(?=[^>]*aria-role="button")(?=[^>]*:aria-label="(?=[^"]*field\.label)(?=[^"]*tagSummary\s*\(\s*field\.key\s*\))[^"]*")[^>]*>/,
  'Accessible tag field action',
)
assertMatch(
  editTemplate,
  /<view\b(?=[^>]*class="profile-edit__tag-sheet-close")(?=[^>]*aria-role="button")(?=[^>]*aria-label="关闭标签选择")[^>]*>/,
  'Accessible tag sheet close',
)
assertMatch(
  editTemplate,
  /<view\b(?=[^>]*class="profile-edit__tag-option")(?=[^>]*aria-role="checkbox")(?=[^>]*:aria-label="option")(?=[^>]*:aria-checked="isTagSelected\(option\)")[^>]*>/,
  'Accessible tag option state',
)
assertStyleBlock(
  editStyle,
  /&__tag-sheet-close\s*(?=\{)/,
  /(?:^|[;\s])width:\s*88rpx\s*;/,
  'Tag sheet close width',
)
assertStyleBlock(
  editStyle,
  /&__tag-sheet-close\s*(?=\{)/,
  /(?:^|[;\s])height:\s*88rpx\s*;/,
  'Tag sheet close height',
)
assertMatch(
  editScript,
  /const\s+tagOptionMemory\s*=\s*reactive\s*<\s*Record\s*<\s*TagKey\s*,\s*string\[\]\s*>\s*>\s*\(/,
  'Tag option memory',
)
assertMatch(activeTagOptionsBody, /return\s+tagOptionMemory\s*\[\s*key\s*\]/, 'Tag options use session memory')
assertEqual(
  [hydrateDraftBody, openTagSheetBody].some(
    (body) =>
      /tagOptionMemory\s*\[[^\]]+\]\s*=/.test(body) &&
      /new Set\s*\(/.test(body) &&
      /tagOptionCatalog\s*\[[^\]]+\]/.test(body) &&
      /(?:profile(?:\.[A-Za-z]+|\s*\[[^\]]+\])|draft\.career(?:\.[A-Za-z]+|\s*\[[^\]]+\]))/.test(body),
  ),
  true,
  'Tag option memory union',
)
assertNoMatch(
  activeTagOptionsBody,
  /\[\s*\.\.\.tagOptionCatalog\s*\[\s*key\s*\]\s*,\s*\.\.\.draft\.career\s*\[\s*key\s*\]\s*\]/,
  'No draft-only tag option source',
)
assertMatch(
  editScript,
  /onBackPress\(\s*\(\)\s*=>\s*\{\s*if\s*\(\s*activeTagField\.value\s*\)\s*\{\s*closeTagSheet\(\)\s*;?\s*return\s+true\s*;?\s*\}\s*if\s*\(\s*!isDirty\.value\s*\)/,
  'Back closes tag sheet first',
)
assertStyleBlock(
  editStyle,
  /&__tag-option\s*(?=\{)/,
  /(?:^|[;\s])height:\s*96rpx\s*;/,
  'Fixed tag option height',
)
assertStyleBlock(editStyle, /&__tag-option-label\s*(?=\{)/, /flex:\s*1\s*;/, 'Flexible tag option label')
assertStyleBlock(editStyle, /&__tag-option-label\s*(?=\{)/, /min-width:\s*0\s*;/, 'Tag option label min width')
assertStyleBlock(editStyle, /&__tag-option-label\s*(?=\{)/, /overflow:\s*hidden\s*;/, 'Tag option label clipping')
assertStyleBlock(
  editStyle,
  /&__tag-option-label\s*(?=\{)/,
  /text-overflow:\s*ellipsis\s*;/,
  'Tag option label ellipsis',
)
assertStyleBlock(editStyle, /&__tag-option-label\s*(?=\{)/, /white-space:\s*nowrap\s*;/, 'Tag option label single line')
assertMatch(hydrateDraftBody, /workLibraryVersion\.value\s*=\s*profile\.workLibraryVersion/, 'Hydrated work library version')
assertMatch(
  navigateToImportReviewBody,
  /setContext\(\s*scene\s*,\s*draft\.expectedProfileVersion\s*,\s*workLibraryVersion\.value\s*,\s*draft\.avatarAssetId\s*\)/,
  'Full-profile import carries versions and current avatar context',
)
assertMatch(
  openImportReviewBody,
  /if\s*\(\s*!isDirty\.value\s*\)[\s\S]*navigateToImportReview\(\)[\s\S]*return/,
  'Clean profile enters import directly',
)
assertMatch(
  openImportReviewBody,
  /isInitialAvatarOnlyDraft\(\)[\s\S]*navigateToImportReview\(\)[\s\S]*return/,
  'Initial avatar-only draft enters import without a complete profile save',
)
assertMatch(
  initialAvatarOnlyDraftBody,
  /draft\.expectedProfileVersion\s*!==\s*0[\s\S]*!draft\.avatarAssetId[\s\S]*!baseline\.value[\s\S]*return\s+false/,
  'Avatar-only shortcut is restricted to a loaded initial profile',
)
assertMatch(
  initialAvatarOnlyDraftBody,
  /snapshotWithoutAvatar\(draft\)\s*===\s*snapshotWithoutAvatar\(savedDraft\)/,
  'Avatar-only shortcut rejects every non-avatar draft change',
)
assertMatch(
  openImportReviewBody,
  /uni\.showActionSheet\(\{[\s\S]*itemList:\s*\[\s*'保存资料并进入'\s*,\s*'保留头像，放弃其他修改并进入'\s*,\s*'继续编辑'\s*\]/,
  'Dirty import uses the native three-way action sheet',
)
assertMatch(
  openImportReviewBody,
  /tapIndex\s*===\s*0[\s\S]*saveProfile\(\)\.then\([\s\S]*if\s*\(\s*saved\s*\)\s*navigateToImportReview\(\)/,
  'Dirty import navigates only after a successful save',
)
assertMatch(
  openImportReviewBody,
  /tapIndex\s*===\s*1[\s\S]*discardUnsavedNonAvatarChanges\(\)[\s\S]*navigateToImportReview\(\)/,
  'Dirty import explicitly discards non-avatar changes before navigating',
)
assertMatch(
  discardNonAvatarDraftBody,
  /const\s+avatarAssetId\s*=\s*draft\.avatarAssetId[\s\S]*restoreBaselineDraft\(\)[\s\S]*draft\.avatarAssetId\s*=\s*avatarAssetId/,
  'Discarding an import draft preserves the chosen avatar only',
)
assertMatch(editScript, /const\s+avatarPreviewRevision\s*=\s*ref\(0\)/, 'Avatar preview request revision')
assertMatch(
  hydrateDraftBody,
  /const\s+requestRevision\s*=\s*\+\+avatarPreviewRevision\.value[\s\S]*selectedAvatarPreview\.value\s*=\s*''[\s\S]*hydrateAvatarPreview\(\s*profile\.avatarAssetId\s*,\s*requestRevision\s*\)/,
  'Saved avatar hydration starts a revision-bound owner preview request',
)
assertMatch(
  hydrateAvatarPreviewBody,
  /requestAssetAccessUrl\(\s*assetId\s*,\s*\{\s*showLoading:\s*false\s*,\s*showError:\s*false\s*,?\s*\}\s*\)/,
  'Avatar preview uses a silent background access-url request',
)
assertMatch(
  hydrateAvatarPreviewBody,
  /requestRevision\s*!==\s*avatarPreviewRevision\.value[\s\S]*draft\.avatarAssetId\s*!==\s*assetId[\s\S]*return[\s\S]*selectedAvatarPreview\.value\s*=\s*access\.accessUrl/,
  'Late saved-avatar preview cannot replace a newer avatar selection',
)
assertMatch(
  onShowBody,
  /if\s*\(\s*selected\s*\)\s*\{[\s\S]*const\s+requestRevision\s*=\s*\+\+avatarPreviewRevision\.value[\s\S]*draft\.avatarAssetId\s*=\s*selected\.assetId[\s\S]*selectedAvatarPreview\.value\s*=\s*''[\s\S]*hydrateAvatarPreview\(selected\.assetId,\s*requestRevision\)/,
  'New avatar selection silently rehydrates a revision-bound preview',
)
assertNoMatch(onShowBody, /selected\.previewUrl|selected\.accessUrl/, 'Profile editor never consumes a stored short-lived avatar URL')
assertMatch(
  onShowBody,
  /consumeApplied\(\)[\s\S]*loadProfile\(\)/,
  'Profile editor reloads after applied import',
)
assertMatch(
  loadProfileBody,
  /getMyCareerProfile\(\{\s*showLoading:\s*false,\s*showError:\s*false\s*\}\)/,
  'Page-owned load error feedback',
)
assertMatch(loadProfileBody, /\btry\s*\{/, 'Profile load try block')
assertMatch(
  loadProfileBody,
  /catch\s*\([^)]*\)\s*\{[\s\S]*?loadError\.value\s*=/,
  'Captured profile load error',
)
assertMatch(loadProfileBody, /hydrateDraft\s*\(/, 'Profile hydration after load')
assertMatch(editTemplate, /v-else-if="loadError"[\s\S]*档案读取失败/, 'Explicit profile load error state')
assertMatch(
  editTemplate,
  /<button\b(?=[^>]*@click="loadProfile")[^>]*>[\s\S]*?重新加载[\s\S]*?<\/button>/,
  'Profile load retry action',
)
assertEqual((editTemplate.match(/@click="saveProfile"/g) || []).length, 1, 'Single profile save action')
assertEqual((editScript.match(/updateMyActorProfile\(/g) || []).length, 1, 'Single profile save request')
assertMatch(
  editScript,
  /itemList:\s*\[\s*'保存资料并返回'\s*,\s*'放弃修改'\s*,\s*'继续编辑'\s*\]/,
  'Dirty leave action sheet',
)
assertStyleBlock(
  editStyle,
  /\.profile-edit\s*(?=\{)/,
  /background:\s*(?:\$kp-color-bg|linear-gradient\([^;{}]*\$kp-color-bg[^;{}]*\))\s*;/i,
  'Profile page uses the shared warm background token',
)
assertStyleBlock(editStyle, /\.profile-edit\s*(?=\{)/, /color:\s*\$kp-color-text-primary\s*;/i, 'Profile page uses shared primary text')
assertMatch(
  editTemplate,
  /class="profile-edit__cell profile-edit__cell--gender"[\s\S]*?>\s*<text class="profile-edit__cell-label">性别<\/text>[\s\S]*?class="profile-edit__segments"/,
  'Gender label and segmented control share one cell row',
)
assertNoMatch(editTemplate, /class="profile-edit__cell profile-edit__cell--stacked"[\s\S]*?>\s*<text class="profile-edit__cell-label">性别<\/text>/, 'Gender row is not vertically stacked')
assertStyleBlock(editStyle, /&__cell\s*(?=\{)/, /min-height:\s*104rpx\s*;/, 'Profile cell remains within the 48-56px height contract')
assertStyleBlock(editStyle, /&__cell--gender\s*(?=\{)/, /gap:\s*24rpx\s*;/, 'Gender row horizontal spacing')
assertStyleBlock(editStyle, /&__segments\s*(?=\{)/, /width:\s*240rpx\s*;/, 'Gender segments use a bounded row width')
assertStyleBlock(editStyle, /&__segments\s*(?=\{)/, /margin-left:\s*auto\s*;/, 'Gender segments align to the row end')
assertStyleBlock(editStyle, /&__save\s*(?=\{)/, /background:\s*\$kp-color-dark-primary\s*;/i, 'Profile primary action uses shared dark surface')
assertStyleBlock(
  editStyle,
  /&__tag-sheet\s*(?=\{)/,
  /border-radius:\s*28rpx\s+28rpx\s+0\s+0\s*;/,
  'Tag sheet top radius',
)
assertWarmProfileTokenContract(edit, editStyle, 'Profile editor')
assertNoMatch(editTemplate, /多个内容用逗号分隔/, 'No comma-entry tag editor')
assertMatch(editScript, /chooseAvatarFromAssets/, 'Avatar asset selection')
assertNoMatch(editTemplate, /完成度|提升建议|AI 全量润色/, 'No profile operation cards')
assertNoMatch(
  edit,
  /updateActorProfile\(|buildPayload\(|workExperiences|photoCategories|videoUrl|resumePdf|PhotoCategorySection|WorkExperienceSection|PdfResumeSection|VideoResumeSection/,
  'Simplified actor profile editor',
)

const importPage = await readText('kaipai-frontend/src/pkg-profile/import-review/index.vue')
const importPageSections = extractSfcSections(importPage, 'Profile import review')
const invalidateExtractionDraftBody = extractFunctionBlock(
  importPageSections.script,
  /function\s+invalidateExtractionDraft\s*\(\s*\)\s*:\s*void/,
  'invalidateExtractionDraft',
)
assertMatch(
  invalidateExtractionDraftBody,
  /importStore\.clearExtractionDraft\(\)/,
  'Page invalidation clears store extraction',
)
assertMatch(
  invalidateExtractionDraftBody,
  /extractionDraftRevision\.value\s*\+=\s*1/,
  'Page invalidation advances extraction revision',
)
for (const state of [
  'profileFinalValues',
  'profileConflictChoices',
  'workFinalFields',
  'workConflictChoices',
]) {
  assertMatch(
    invalidateExtractionDraftBody,
    new RegExp(`${state}\\.value\\s*=\\s*\\{\\}`),
    `Page invalidation clears ${state}`,
  )
}
const submitExtractionBody = extractFunctionBlock(
  importPageSections.script,
  /async\s+function\s+submitExtraction\s*\(\s*\)\s*:\s*Promise<void>/,
  'submitExtraction',
)
const beginClipboardReadBody = extractFunctionBlock(
  importPageSections.script,
  /async\s+function\s+beginClipboardRead\s*\(\s*\)\s*:\s*Promise<void>/,
  'beginClipboardRead',
)
const applyReviewBody = extractFunctionBlock(
  importPageSections.script,
  /async\s+function\s+applyReview\s*\(\s*\)\s*:\s*Promise<void>/,
  'applyReview',
)
assertMatch(
  applyReviewBody,
  /\.\.\.\(\s*importStore\.scene\s*===\s*'full_profile'\s*\?\s*\{\s*avatarAssetId:\s*importStore\.avatarAssetId\s*\}\s*:\s*\{\s*\}\s*\)/,
  'Apply request includes avatar context only for full-profile imports',
)
assertEqual(
  (applyReviewBody.match(/avatarAssetId\s*:/g) || []).length,
  1,
  'Apply request has no unconditional avatar field',
)
const goBackBody = extractFunctionBlock(
  importPageSections.script,
  /function\s+goBack\s*\(\s*\)\s*:\s*void/,
  'goBack',
)
const destructiveClipboardReviewStatePattern = new RegExp([
  String.raw`rawText\.value\s*=`,
  String.raw`importStore\.setRawText\s*\(`,
  String.raw`importStore\.clear\s*\(`,
  String.raw`importStore\.clearExtractionDraft\s*\(`,
  String.raw`(?:^|[^\w.])clearExtractionDraft\s*\(`,
  String.raw`invalidateExtractionDraft\s*\(`,
  String.raw`profileFinalValues\.value\s*=`,
  String.raw`profileConflictChoices\.value\s*=`,
  String.raw`workFinalFields\.value\s*=`,
  String.raw`workConflictChoices\.value\s*=`,
].join('|'))

function assertPreservesClipboardReviewState(source, label) {
  assertNoMatch(source, destructiveClipboardReviewStatePattern, label)
}

const destructiveClipboardReviewStateMutations = [
  ['direct source write', 'rawText.value = nextRawText'],
  ['store source write', 'importStore.setRawText(nextRawText)'],
  ['store clear', 'importStore.clear()'],
  ['store extraction clear', 'importStore.clearExtractionDraft()'],
  ['direct extraction clear', 'clearExtractionDraft()'],
  ['page draft invalidation', 'invalidateExtractionDraft()'],
  ['profile final values reset', 'profileFinalValues.value = {}'],
  ['profile conflict choices reset', 'profileConflictChoices.value = {}'],
  ['work final fields reset', 'workFinalFields.value = {}'],
  ['work conflict choices reset', 'workConflictChoices.value = {}'],
]
for (const [label, mutation] of destructiveClipboardReviewStateMutations) {
  let rejected = false
  try {
    assertPreservesClipboardReviewState(mutation, `${label} mutation`)
  } catch {
    rejected = true
  }
  assertEqual(rejected, true, `${label} destructive mutation turns the clipboard guard RED`)
}

assertMatch(
  importPageSections.script,
  /set:\s*\(value:\s*string\)\s*=>\s*\{[\s\S]*?invalidateExtractionDraft\(\)[\s\S]*?importStore\.setRawText\(value\)/,
  'Editing source invalidates prior extraction',
)
assertMatch(
  beginClipboardReadBody,
  /const\s+requestRevision\s*=\s*extractionDraftRevision\.value[\s\S]*await\s+uni\.getClipboardData\(\)[\s\S]*const\s+nextRawText\s*=\s*String\(result\.data\s*\|\|\s*''\)\.trim\(\)/,
  'Clipboard read invalidates prior review only through a successful source replacement',
)
assertPreservesClipboardReviewState(
  beginClipboardReadBody.slice(0, beginClipboardReadBody.indexOf('await uni.getClipboardData()')),
  'Clipboard read preserves the current extraction until the platform read succeeds',
)
assertMatch(
  beginClipboardReadBody,
  /await\s+uni\.getClipboardData\(\)[\s\S]*if\s*\([^)]*!pageActive\.value[^)]*requestRevision\s*!==\s*extractionDraftRevision\.value[^)]*\)\s*return[\s\S]*const\s+nextRawText\s*=/,
  'Clipboard result cannot repopulate source after unload or source revision change',
)
const emptyClipboardBody = extractFunctionBlock(
  beginClipboardReadBody,
  /if\s*\(\s*!nextRawText\s*\)/,
  'empty clipboard guard',
)
assertMatch(
  emptyClipboardBody,
  /extractionError\.value\s*=\s*'剪贴板内容为空，请复制文字后重试'[\s\S]*return/,
  'Empty clipboard reports a page-owned error',
)
assertPreservesClipboardReviewState(
  emptyClipboardBody,
  'Empty clipboard preserves source extraction and final choices',
)
const unchangedClipboardBody = extractFunctionBlock(
  beginClipboardReadBody,
  /if\s*\(\s*nextRawText\s*===\s*rawText\.value\.trim\(\)\s*\)/,
  'unchanged clipboard guard',
)
assertMatch(
  unchangedClipboardBody,
  /extractionError\.value\s*=\s*''[\s\S]*return/,
  'Unchanged clipboard clears an old clipboard error without replacing source',
)
assertPreservesClipboardReviewState(
  unchangedClipboardBody,
  'Unchanged clipboard preserves extraction and final choices',
)
assertEqual(
  (beginClipboardReadBody.match(/rawText\.value\s*=\s*nextRawText/g) || []).length,
  1,
  'Clipboard has one guarded source replacement',
)
const clipboardNormalizeIndex = beginClipboardReadBody.indexOf('const nextRawText')
const emptyClipboardGuardIndex = beginClipboardReadBody.indexOf('if (!nextRawText)')
const unchangedClipboardGuardIndex = beginClipboardReadBody.indexOf('if (nextRawText === rawText.value.trim())')
const clipboardReplacementIndex = beginClipboardReadBody.indexOf('rawText.value = nextRawText')
assertEqual(
  clipboardNormalizeIndex >= 0
    && clipboardNormalizeIndex < emptyClipboardGuardIndex
    && emptyClipboardGuardIndex < unchangedClipboardGuardIndex
    && unchangedClipboardGuardIndex < clipboardReplacementIndex,
  true,
  'Clipboard guards empty and unchanged text before invalidating replacement',
)
const clipboardReadCatchBody = extractFunctionBlock(
  beginClipboardReadBody,
  /catch\s*\([^)]*\)/,
  'beginClipboardRead catch',
)
assertMatch(
  clipboardReadCatchBody,
  /requestRevision\s*===\s*extractionDraftRevision\.value[\s\S]*extractionError\.value\s*=\s*'读取剪贴板失败，请重试'/,
  'Current clipboard read failure reports a page-owned error',
)
assertPreservesClipboardReviewState(
  clipboardReadCatchBody,
  'Clipboard failure preserves the current extraction and final choices',
)
assertMatch(
  beginClipboardReadBody,
  /finally\s*\{\s*if\s*\(\s*pageActive\.value\s*\)\s*readingClipboard\.value\s*=\s*false/,
  'Clipboard finally cannot mutate a destroyed page',
)
assertMatch(
  submitExtractionBody,
  /invalidateExtractionDraft\(\)[\s\S]*await\s+extractProfileImport\(/,
  'New extraction invalidates prior review before request',
)
assertMatch(
  submitExtractionBody,
  /const\s+requestRevision\s*=\s*extractionDraftRevision\.value[\s\S]*await\s+extractProfileImport\([\s\S]*if\s*\(requestRevision\s*!==\s*extractionDraftRevision\.value\)\s*return[\s\S]*importStore\.setExtraction\(result\)/,
  'Edited source cannot accept stale in-flight extraction',
)
assertMatch(importPageSections.script, /const\s+pageActive\s*=\s*ref\(true\)/, 'Explicit page-active state')
assertMatch(importPageSections.script, /const\s+applyRevision\s*=\s*ref\(0\)/, 'Apply request revision')
const isCurrentApplyBody = extractFunctionBlock(
  importPageSections.script,
  /function\s+isCurrentApply\s*\(\s*requestRevision:\s*number\s*\)\s*:\s*boolean/,
  'isCurrentApply',
)
assertMatch(isCurrentApplyBody, /pageActive\.value/, 'Current apply requires an active page')
assertMatch(
  isCurrentApplyBody,
  /requestRevision\s*===\s*applyRevision\.value/,
  'Current apply requires the latest request revision',
)
assertMatch(
  applyReviewBody,
  /const\s+requestRevision\s*=\s*\+\+applyRevision\.value[\s\S]*await\s+applyProfileImport\(payload\)[\s\S]*importStore\.markApplied\(\)[\s\S]*if\s*\(\s*!isCurrentApply\(requestRevision\)\s*\)\s*return[\s\S]*importStore\.clear\(\)/,
  'Late apply success preserves the parent refresh signal without clearing a future page',
)
assertNoMatch(
  applyReviewBody.slice(
    applyReviewBody.indexOf('if (!isCurrentApply(requestRevision)) return'),
    applyReviewBody.indexOf('importStore.clear()'),
  ),
  /uni\.showToast|uni\.navigateBack/,
  'Apply page UI remains behind the active-page gate',
)
const applyReviewCatchBody = extractFunctionBlock(
  applyReviewBody,
  /catch\s*\([^)]*\)/,
  'applyReview catch',
)
assertMatch(
  applyReviewCatchBody,
  /if\s*\(\s*!isCurrentApply\(requestRevision\)\s*\)\s*return/,
  'Inactive apply failure is ignored',
)
assertMatch(
  applyReviewCatchBody,
  /extractionError\.value\s*=\s*mapProfileImportError\([^)]*\)/,
  'Active apply failure uses one code-mapped feedback message',
)
assertEqual(
  (applyReviewCatchBody.match(/uni\.showToast\(/g) || []).length,
  0,
  'Apply failure has no duplicate Toast',
)
assertNoMatch(
  applyReviewCatchBody,
  /importStore\.clear|invalidateExtractionDraft|clearExtractionDraft/,
  'Apply failure preserves candidates',
)
assertMatch(
  applyReviewBody,
  /setTimeout\s*\(\s*\(\)\s*=>\s*\{[\s\S]*?if\s*\(\s*!isCurrentApply\(requestRevision\)\s*\)\s*return[\s\S]*?uni\.navigateBack\(\)/,
  'Delayed apply navigation is page/revision guarded',
)
for (const [signature, label] of [
  [/async\s+function\s+beginClipboardRead\s*\(\s*\)\s*:\s*Promise<void>/, 'Clipboard read'],
  [/async\s+function\s+submitExtraction\s*\(\s*\)\s*:\s*Promise<void>/, 'Extraction'],
  [/function\s+toggleProfileCandidate\s*\([^)]*\)\s*:\s*void/, 'Profile selection'],
  [/function\s+confirmInferredCandidate\s*\([^)]*\)\s*:\s*void/, 'Inferred confirmation'],
  [/function\s+selectProfileConflictValue\s*\([^)]*\)\s*:\s*void/, 'Profile conflict selection'],
  [/function\s+toggleWorkCandidate\s*\([^)]*\)\s*:\s*void/, 'Work selection'],
  [/function\s+selectWorkConflictValue\s*\([^)]*\)\s*:\s*void/, 'Work conflict selection'],
]) {
  const body = extractFunctionBlock(importPageSections.script, signature, label)
  assertMatch(body, /if\s*\([^)]*applying\.value[^)]*\)\s*return/, `${label} is locked during apply`)
}
assertMatch(goBackBody, /if\s*\(\s*applying\.value\s*\)\s*return/, 'Back action is locked during apply')
assertMatch(
  importPageSections.script,
  /onBackPress\(\s*\(\)\s*=>\s*\{\s*if\s*\(\s*!applying\.value\s*\)\s*return\s+false\s*;?\s*return\s+true/,
  'System back is locked during apply',
)
assertMatch(
  importPageSections.script,
  /set:\s*\(value:\s*string\)\s*=>\s*\{\s*if\s*\(\s*applying\.value\s*\)\s*return/,
  'Source editing is locked during apply',
)
assertMatch(
  importPageSections.template,
  /<textarea\b(?=[^>]*:disabled="applying")[^>]*>/,
  'Source textarea exposes apply lock state',
)
assertMatch(importPage, /beginClipboardRead[\s\S]*uni\.getClipboardData/, 'Explicit clipboard read')
assertNoMatch(importPage, /onLoad\([^)]*=>[\s\S]{0,300}getClipboardData/, 'No automatic clipboard read')
assertMatch(importPage, /async function submitExtraction\(\)[\s\S]*extractProfileImport/, 'Explicit extraction action')
assertMatch(importPage, /requiresExplicitConfirmation[\s\S]*confirmed/, 'Explicit inferred candidate confirmation')
assertMatch(importPage, /个人资料[\s\S]*作品[\s\S]*需要确认[\s\S]*疑似重复[\s\S]*未映射内容/, 'Import review groups')
const profileGroupStart = importPageSections.template.indexOf('>个人资料</text>')
const workGroupStart = importPageSections.template.indexOf('>作品</text>', profileGroupStart + 1)
const confirmationGroupStart = importPageSections.template.indexOf('>需要确认</text>', workGroupStart + 1)
const duplicateGroupStart = importPageSections.template.indexOf('>疑似重复</text>', confirmationGroupStart + 1)
const unmappedGroupStart = importPageSections.template.indexOf('>未映射内容</text>', duplicateGroupStart + 1)
assertEqual(
  [profileGroupStart, workGroupStart, confirmationGroupStart, duplicateGroupStart, unmappedGroupStart]
    .every((value, index, values) => value >= 0 && (index === 0 || value > values[index - 1])),
  true,
  'Ordered import review section boundaries',
)
const profileGroupTemplate = importPageSections.template.slice(profileGroupStart, workGroupStart)
const workGroupTemplate = importPageSections.template.slice(workGroupStart, confirmationGroupStart)
const confirmationGroupTemplate = importPageSections.template.slice(confirmationGroupStart, duplicateGroupStart)
const duplicateGroupTemplate = importPageSections.template.slice(duplicateGroupStart, unmappedGroupStart)
const unmappedGroupTemplate = importPageSections.template.slice(unmappedGroupStart)
assertMatch(
  importPageSections.script,
  /REVIEW_PROFILE_STATUSES[\s\S]*'conflict'[\s\S]*'low_confidence'[\s\S]*'derived'[\s\S]*'unreadable'/,
  'Review-required profile statuses',
)
assertMatch(
  importPageSections.script,
  /requiresProfileReview[\s\S]*candidate\.conflict/,
  'Profile conflicts always enter the confirmation group',
)
assertMatch(importPageSections.script, /regularProfileCandidates[\s\S]*!requiresProfileReview/, 'Regular profile grouping')
assertMatch(importPageSections.script, /reviewProfileCandidates[\s\S]*requiresProfileReview/, 'Review profile grouping')
assertMatch(importPageSections.script, /newWorkCandidates[\s\S]*matchStatus\s*===\s*'new'/, 'New work grouping')
assertMatch(importPageSections.script, /duplicateWorkCandidates[\s\S]*matchStatus\s*!==\s*'new'/, 'Duplicate work grouping')
assertMatch(profileGroupTemplate, /v-for="candidate in regularProfileCandidates"/, 'Personal profile group data source')
assertMatch(workGroupTemplate, /v-for="work in newWorkCandidates"/, 'New work group data source')
assertMatch(
  confirmationGroupTemplate,
  /v-for="candidate in reviewProfileCandidates"/,
  'Needs-confirmation group data source',
)
assertMatch(profileGroupTemplate, /reviewStatus\s*===\s*'unchanged'[\s\S]*无需修改/, 'Unchanged profile status')
assertMatch(
  profileGroupTemplate,
  /:disabled="applying\s*\|\|\s*isUnchangedCandidate\(candidate\)"/,
  'Unchanged profile candidate cannot be selected',
)
const toggleProfileCandidateBody = extractFunctionBlock(
  importPageSections.script,
  /function\s+toggleProfileCandidate\s*\([^)]*\)\s*:\s*void/,
  'toggleProfileCandidate',
)
assertMatch(toggleProfileCandidateBody, /isUnchangedCandidate\(candidate\)/, 'Unchanged profile selection guard')
assertMatch(duplicateGroupTemplate, /v-for="work in duplicateWorkCandidates"/, 'Duplicate group data source')
assertNoMatch(
  importPageSections.template,
  /v-for="work in extraction\.workCandidates"/,
  'No ungrouped work candidates',
)
assertMatch(
  unmappedGroupTemplate,
  /v-for="(?:segment|\(segment,\s*index\)) in extraction\.unmappedSegments"/,
  'Unmapped segments are rendered individually',
)
assertMatch(unmappedGroupTemplate, /ignoredMediaPlaceholderCount/, 'Media placeholders remain separately visible')
for (const field of [
  'projectName',
  'roleName',
  'publishStatus',
  'workTypeCode',
  'roleLevelCode',
  'shootYear',
  'shootMonth',
  'platform',
  'syncSoundStatus',
  'collaborators',
  'achievementText',
  'description',
]) {
  assertMatch(importPageSections.script, new RegExp(`key:\\s*'${field}'`), `Visible work field ${field}`)
}
assertMatch(importPageSections.template, /visibleWorkFields\(work\)/, 'All populated work fields are rendered')
assertMatch(
  importPageSections.template,
  /formatProfileImportValue\(candidate\.fieldKey,/,
  'Profile enum values use display-only labels',
)
assertMatch(
  importPageSections.template,
  /formatWorkImportValue\(field\.key,\s*field\.value\)/,
  'Work enum values use display-only labels',
)
const profileEnumLabelsBody = extractFunctionBlock(
  importPageSections.script,
  /const\s+PROFILE_ENUM_VALUE_LABELS[^=]*=/,
  'PROFILE_ENUM_VALUE_LABELS',
)
const workEnumLabelsBody = extractFunctionBlock(
  importPageSections.script,
  /const\s+WORK_ENUM_VALUE_LABELS[^=]*=/,
  'WORK_ENUM_VALUE_LABELS',
)
for (const [field, values, source] of [
  ['gender', ['male', 'female'], profileEnumLabelsBody],
  ['birth_precision', ['year', 'month', 'day'], profileEnumLabelsBody],
  ['publishStatus', ['aired', 'upcoming', 'stage', 'horizontal', 'other'], workEnumLabelsBody],
  [
    'workTypeCode',
    [
      'short_drama', 'horizontal_short_drama', 'stage_play', 'musical', 'tv_column_drama',
      'film_tv', 'micro_film', 'horizontal', 'stage', 'other',
    ],
    workEnumLabelsBody,
  ],
  [
    'roleLevelCode',
    [
      'lead', 'supporting', 'antagonist', 'female_lead', 'female_supporting_1',
      'female_supporting_2', 'female_antagonist_1', 'male_lead', 'male_supporting_1',
      'male_supporting_2', 'male_antagonist_1', 'other',
    ],
    workEnumLabelsBody,
  ],
  ['syncSoundStatus', ['sync', 'dubbed', 'unknown'], workEnumLabelsBody],
]) {
  const fieldLabelsBody = extractFunctionBlock(source, new RegExp(`\\b${field}\\s*:`), `${field} labels`)
  for (const value of values) {
    assertMatch(fieldLabelsBody, new RegExp(`\\b${value}:`), `${field} display label ${value}`)
  }
}
const formatProfileImportValueBody = extractFunctionBlock(
  importPageSections.script,
  /function\s+formatProfileImportValue\s*\([^)]*\)\s*:\s*string/,
  'formatProfileImportValue',
)
const formatWorkImportValueBody = extractFunctionBlock(
  importPageSections.script,
  /function\s+formatWorkImportValue\s*\([^)]*\)\s*:\s*string/,
  'formatWorkImportValue',
)
assertNoMatch(
  `${formatProfileImportValueBody}\n${formatWorkImportValueBody}`,
  /profileFinalValues|workFinalFields|candidateValue\s*=/,
  'Display labels cannot mutate raw apply values',
)
assertMatch(
  importPageSections.script,
  /result\.profileCandidates\.map\(\(candidate\)\s*=>\s*\[candidate\.candidateId,\s*candidate\.candidateValue\]\)/,
  'Profile apply draft retains raw candidate values',
)
assertMatch(
  importPageSections.script,
  /result\.workCandidates\.map\(\(work\)\s*=>\s*\[work\.candidateId,\s*copyProfileImportWorkFields\(work\)\]\)/,
  'Work apply draft retains raw candidate values',
)
assertMatch(importPageSections.template, /field\.sourceText/, 'Per-field work evidence')
assertMatch(importPageSections.template, /field\.warning/, 'Per-field work warning')
assertMatch(importPageSections.template, /workMatchStatusLabel\(work\.matchStatus\)/, 'Visible work match status')
assertNoMatch(importPageSections.script, /function\s+workSourceText/, 'No single aggregated work evidence fallback')
assertMatch(
  importPageSections.script,
  /onUnload\(\(\)\s*=>\s*\{[\s\S]*pageActive\.value\s*=\s*false[\s\S]*applyRevision\.value\s*\+=\s*1[\s\S]*invalidateExtractionDraft\(\)[\s\S]*importStore\.clear\(\)/,
  'Import unload invalidates in-flight extraction and fully clears source',
)
const mapProfileImportErrorBody = extractFunctionBlock(
  importPageSections.script,
  /function\s+mapProfileImportError\s*\(\s*error:\s*unknown\s*\)\s*:\s*string/,
  'mapProfileImportError',
)
for (let code = 46001; code <= 46017; code += 1) {
  assertMatch(importPageSections.script, new RegExp(`\\b${code}:`), `Profile import numeric error ${code}`)
}
assertMatch(mapProfileImportErrorBody, /PROFILE_IMPORT_ERROR_MESSAGES\[error\.code\]/, 'Numeric profile import error lookup')
assertNoMatch(mapProfileImportErrorBody, /error\.(?:errorCode|message)/, 'Known errors do not depend on response text')
assertNoMatch(importPageSections.script, /capability\.reason/, 'No legacy capability reason fallback')
assertMatch(importPage, /applyProfileImport[\s\S]*markApplied\(\)/, 'Applied import refresh signal')
assertMatch(importPage, /buildProfileImportApplyRequest/, 'Profile import apply builder usage')
assertMatch(importPageSections.template, /sourceText/, 'Human-readable source evidence')
assertNoMatch(importPageSections.template, /candidateProof/, 'Candidate proof is not rendered as evidence')
assertNoMatch(
  importPageSections.template,
  /v-model="(?:candidate\.candidateValue|work\.(?:projectName|roleName))"/,
  'Signed extraction values remain read-only',
)
assertNoMatch(importPage, /:\s*any\b|as any\b/, 'Typed profile import review')
function assertImportReviewNeutralShell(source, label) {
  const sections = extractSfcSections(source, `${label} SFC`)
  assertNeutralProfilePackageShell(source, sections, 'import-review', label, {
    groupSelectors: [/\.import-review__source,\s*\.import-review__group\s*/],
    primaryActionSelectors: [/\.import-review__primary,\s*\.import-review__apply\s*/],
    buttonSelectors: [/\.import-review__primary,\s*\.import-review__secondary,\s*\.import-review__apply,\s*\.import-review__confirm\s*/],
  })
  assertStyleBlock(sections.style, /\.import-review__footer\s*/, /position:\s*fixed\s*;/, `${label} keeps a fixed action footer`)
  assertStyleBlock(sections.style, /\.import-review__footer\s*/, /bottom:\s*0\s*;/, `${label} pins the action footer to the viewport bottom`)
  assertStyleBlock(
    sections.style,
    /\.import-review__footer\s*/,
    /padding:\s*14rpx\s+\$kp-spacing-page\s+calc\(14rpx\s*\+\s*env\(safe-area-inset-bottom\)\)\s*;/,
    `${label} action footer reserves the bottom safe area`,
  )
  assertStyleBlock(
    sections.style,
    /\.import-review__bottom-space\s*/,
    /height:\s*calc\(118rpx\s*\+\s*env\(safe-area-inset-bottom\)\)\s*;/,
    `${label} reserves the exact fixed-footer clearance`,
  )
}
assertImportReviewNeutralShell(importPage, 'Profile import review')

const worksPage = await readText('kaipai-frontend/src/pkg-profile/works/index.vue')
const worksPageSections = extractSfcSections(worksPage, 'Work library SFC')
const actorWorkApi = await readText('kaipai-frontend/src/api/actor-work.ts')
assertMatch(worksPage, /const PAGE_SIZE\s*=\s*10/, 'Ten-item work pages')
assertMatch(worksPage, /loadNextPage/, 'Paged work loading')
assertMatch(worksPage, /keyword[\s\S]*publishStatus[\s\S]*workTypeCode/, 'Work filters')
assertMatch(worksPage, /getRepresentativeWorks[\s\S]*setRepresentativeWorks/, 'Representative work editing')
assertMatch(worksPage, /deleteActorWork[\s\S]*PROFILE_WORK_IN_USE/, 'Protected work deletion')
assertNoMatch(worksPage, /MAX_WORK_EXPERIENCES|最多 10 条|:\s*any\b|as any\b/, 'Unlimited typed work library')

function assertPatternPrecedes(source, beforePattern, afterPattern, label) {
  const beforeIndex = source.search(beforePattern)
  const afterIndex = source.search(afterPattern)
  if (beforeIndex < 0) throw new Error(`${label}: expected guard ${beforePattern} to match`)
  if (afterIndex < 0) throw new Error(`${label}: expected state write ${afterPattern} to match`)
  if (beforeIndex >= afterIndex) throw new Error(`${label}: guard must precede the state write`)
}

function assertWriteConfinedToGuard(source, guardPattern, writePattern, label) {
  const guardBody = extractFunctionBlock(source, guardPattern, label)
  assertMatch(guardBody, writePattern, `${label} contains the state write`)
  assertNoMatch(source.replace(guardBody, ''), writePattern, `${label} has no state write outside the guard`)
}

function normalizeContractCode(source) {
  return source
    .replace(/\/\*[\s\S]*?\*\//g, '')
    .replace(/\/\/[^\r\n]*/g, '')
    .replace(/\s+/g, ' ')
    .trim()
}

function assertCompleteFunctionBody(source, expected, label) {
  assertEqual(normalizeContractCode(source), normalizeContractCode(expected), label)
}

function findClosingBrace(source, openingBrace, label) {
  let depth = 1
  for (let index = openingBrace + 1; index < source.length; index += 1) {
    if (source[index] === '{') depth += 1
    if (source[index] === '}') depth -= 1
    if (depth === 0) return index
  }
  throw new Error(`${label}: guard block is unterminated`)
}

function extractOnlyTopLevelGuardBody(source, guardPattern, label) {
  const trimmed = source.trim()
  const guardMatch = guardPattern.exec(trimmed)
  if (!guardMatch || guardMatch.index !== 0) {
    throw new Error(`${label}: current guard must be the only top-level statement`)
  }
  const openingBrace = trimmed.indexOf('{', guardMatch.index + guardMatch[0].length)
  if (openingBrace < 0) throw new Error(`${label}: current guard has no block`)
  const closingBrace = findClosingBrace(trimmed, openingBrace, label)
  if (trimmed.slice(closingBrace + 1).trim()) {
    throw new Error(`${label}: current guard must be the only top-level statement`)
  }
  return trimmed.slice(openingBrace + 1, closingBrace)
}

function extractRemainderAfterSingleAwait(source, awaitPattern, label) {
  const awaitMatches = source.match(/\bawait\b/g) || []
  assertEqual(awaitMatches.length, 1, `${label} has exactly one await`)
  const awaitMatch = awaitPattern.exec(source)
  if (!awaitMatch) throw new Error(`${label}: expected await statement ${awaitPattern} to match`)
  if (source.slice(0, awaitMatch.index).trim()) {
    throw new Error(`${label}: await must be the first top-level statement`)
  }
  return source.slice(awaitMatch.index + awaitMatch[0].length)
}

function collectRefStateWrites(source) {
  return [...source.matchAll(/\b([A-Za-z_$][\w$]*)\.value\s*(?:=|\+=|-=|\+\+|--)/g)]
    .map((match) => match[1])
}

function assertActorWorkSilentReadOptions(source, label) {
  assertMatch(
    source,
    /import\s*\{[^}]*\btype\s+RequestOptions\b[^}]*\}\s*from\s*['"]@\/utils\/request['"]\s*;/,
    `${label} imports RequestOptions`,
  )
  const listBody = extractFunctionBlock(
    source,
    /export\s+function\s+getActorWorks\s*\(\s*query:\s*ActorWorkQuery\s*,\s*options\?:\s*Pick<RequestOptions,\s*'showLoading'\s*\|\s*'showError'>\s*,?\s*\)\s*:\s*Promise<PageResult<ActorWork>>/,
    `${label} list read`,
  )
  assertCompleteFunctionBody(
    listBody,
    "return get('/api/actor/works', query as unknown as Record<string, unknown>, options);",
    `${label} forwards list read options`,
  )
  const representativeBody = extractFunctionBlock(
    source,
    /export\s+function\s+getRepresentativeWorks\s*\(\s*options\?:\s*Pick<RequestOptions,\s*'showLoading'\s*\|\s*'showError'>\s*,?\s*\)\s*:\s*Promise<ActorWork\[\]>/,
    `${label} representative read`,
  )
  assertCompleteFunctionBody(
    representativeBody,
    "return get('/api/actor/works/representatives', undefined, options);",
    `${label} forwards representative read options`,
  )
}

const workRequestStateMutationStartCount = functionScopedMutationCount

assertActorWorkSilentReadOptions(actorWorkApi, 'Actor work silent reads')
assertMutationTurnsGateRed(
  actorWorkApi,
  /(return\s+get\(\s*['"]\/api\/actor\/works['"]\s*,\s*query\s+as\s+unknown\s+as\s+Record<string,\s*unknown>)\s*,\s*options\s*\)\s*;/,
  '$1);',
  assertActorWorkSilentReadOptions,
  'actor work list read option forwarding removal',
  { requireUnique: true, expectedFailurePattern: /forwards list read options/ },
)
assertMutationTurnsGateRed(
  actorWorkApi,
  /(return\s+get\(\s*['"]\/api\/actor\/works\/representatives['"]\s*,\s*undefined)\s*,\s*options\s*\)\s*;/,
  '$1);',
  assertActorWorkSilentReadOptions,
  'actor representative read option forwarding removal',
  { requireUnique: true, expectedFailurePattern: /forwards representative read options/ },
)

function assertWorkListRequestRecovery(source, label) {
  const sections = extractSfcSections(source, `${label} SFC`)
  assertMatch(
    sections.script,
    /let\s+workListRevision\s*=\s*0\s*;/,
    `${label} declares a monotonic request revision`,
  )
  assertMatch(
    sections.script,
    /let\s+representativeRevision\s*=\s*0\s*;/,
    `${label} declares a representative request revision`,
  )
  assertMatch(sections.script, /const\s+loadError\s*=\s*ref\(['"]['"]\)\s*;/, `${label} exposes an inline load error`)
  assertMatch(
    sections.script,
    /const\s+pendingPageRetry\s*=\s*ref<PendingWorkPageRetry\s*\|\s*null>\(null\)\s*;/,
    `${label} stores a retryable failed page`,
  )
  assertMatch(
    sections.template,
    /v-if="loadError"[\s\S]*\{\{\s*loadError\s*\}\}[\s\S]*@click="retryWorkList"[\s\S]*重新加载/,
    `${label} renders an inline reload command`,
  )
  assertStyleBlock(sections.style, /\.works-page__error\s*/, /background:\s*\$kp-color-card\s*;/i, `${label} error row uses the shared card surface`)

  assertMatch(
    sections.template,
    /<input\b(?=[^>]*\bv-model="keywordInput")(?=[^>]*@confirm="applyFilters")[^>]*>/,
    `${label} binds an independent keyword draft and commits it on confirm`,
  )
  assertNoMatch(
    sections.template,
    /<input\b[^>]*\bv-model="filters\.keyword"[^>]*>/,
    `${label} never binds the search field to the applied keyword`,
  )
  assertMatch(sections.template, /<picker\b[^>]*@change="changePublishStatus"/, `${label} wires the publish-status picker`)
  assertMatch(sections.template, /<picker\b[^>]*@change="changeWorkType"/, `${label} wires the work-type picker`)
  const templateApplyFilterBindings = [...sections.template.matchAll(/@([\w:-]+)="applyFilters"/g)]
    .map((match) => match[1])
  assertEqual(templateApplyFilterBindings, ['confirm'], `${label} exposes keyword submission only on search confirm`)

  const applyFiltersBody = extractFunctionBlock(
    sections.script,
    /function\s+applyFilters\s*\(\s*\)\s*:\s*void/,
    `${label} search confirmation`,
  )
  assertCompleteFunctionBody(
    applyFiltersBody,
    `
      filters.keyword = keywordInput.value;
      void refreshWorks();
    `,
    `${label} search confirmation has the complete keyword-only allowlist`,
  )

  const changePublishStatusBody = extractFunctionBlock(
    sections.script,
    /function\s+changePublishStatus\s*\([^)]*\)\s*:\s*void/,
    `${label} publish-status picker`,
  )
  assertCompleteFunctionBody(
    changePublishStatusBody,
    `
      filters.publishStatus = publishOptions[Number(event.detail.value)]?.value || '';
      void refreshWorks();
    `,
    `${label} publish-status picker has the complete status-only allowlist`,
  )

  const changeWorkTypeBody = extractFunctionBlock(
    sections.script,
    /function\s+changeWorkType\s*\([^)]*\)\s*:\s*void/,
    `${label} work-type picker`,
  )
  assertCompleteFunctionBody(
    changeWorkTypeBody,
    `
      filters.workTypeCode = typeOptions[Number(event.detail.value)]?.value || '';
      void refreshWorks();
    `,
    `${label} work-type picker has the complete type-only allowlist`,
  )

  const snapshotBody = extractFunctionBlock(
    sections.script,
    /function\s+snapshotWorkFilters\s*\(\s*\)\s*:\s*WorkFilterSnapshot/,
    `${label} filter snapshot`,
  )
  assertMatch(snapshotBody, /keyword:\s*filters\.keyword\s*,/, `${label} snapshots keyword`)
  assertMatch(snapshotBody, /publishStatus:\s*filters\.publishStatus\s*,/, `${label} snapshots publish status`)
  assertMatch(snapshotBody, /workTypeCode:\s*filters\.workTypeCode\s*,/, `${label} snapshots work type`)
  assertCompleteFunctionBody(
    snapshotBody,
    `
      return {
        keyword: filters.keyword,
        publishStatus: filters.publishStatus,
        workTypeCode: filters.workTypeCode,
      };
    `,
    `${label} filter snapshot has the complete side-effect-free allowlist`,
  )

  const filtersMatchBody = extractFunctionBlock(
    sections.script,
    /function\s+filtersMatch\s*\(\s*snapshot:\s*WorkFilterSnapshot\s*\)\s*:\s*boolean/,
    `${label} filter match`,
  )
  assertCompleteFunctionBody(
    filtersMatchBody,
    `
      return filters.keyword === snapshot.keyword
        && filters.publishStatus === snapshot.publishStatus
        && filters.workTypeCode === snapshot.workTypeCode;
    `,
    `${label} filter predicate has the complete three-field allowlist`,
  )

  const currentRequestBody = extractFunctionBlock(
    sections.script,
    /function\s+isCurrentWorkListRequest\s*\(\s*requestRevision:\s*number\s*,\s*requestedFilters:\s*WorkFilterSnapshot\s*\)\s*:\s*boolean/,
    `${label} current request guard`,
  )
  assertCompleteFunctionBody(
    currentRequestBody,
    `return requestRevision === workListRevision && filtersMatch(requestedFilters);`,
    `${label} current-list predicate has the complete revision-and-filter allowlist`,
  )

  const currentPageBody = extractFunctionBlock(
    sections.script,
    /function\s+isCurrentWorkPageRequest\s*\(\s*requestRevision:\s*number\s*,\s*requestedPage:\s*number\s*,\s*requestedFilters:\s*WorkFilterSnapshot\s*\)\s*:\s*boolean/,
    `${label} current page guard`,
  )
  assertCompleteFunctionBody(
    currentPageBody,
    `
      return isCurrentWorkListRequest(requestRevision, requestedFilters)
        && requestedPage === page.value + 1;
    `,
    `${label} current-page predicate has the complete list-and-next-page allowlist`,
  )

  const refreshBody = extractFunctionBlock(
    sections.script,
    /async\s+function\s+refreshWorks\s*\(\s*\)\s*:\s*Promise<void>/,
    `${label} refresh`,
  )
  assertNoMatch(
    refreshBody,
    /if\s*\([^)]*loading\.value[^)]*\)\s*return/,
    `${label} refresh never waits for an older loading flag`,
  )
  assertMatch(
    refreshBody,
    /^\s*const\s+requestRevision\s*=\s*\+\+workListRevision\s*;/,
    `${label} refresh increments revision before state changes`,
  )
  assertMatch(refreshBody, /const\s+requestedFilters\s*=\s*snapshotWorkFilters\(\)\s*;/, `${label} refresh snapshots filters`)
  const refreshTryIndex = refreshBody.search(/\btry\s*\{/)
  if (refreshTryIndex < 0) throw new Error(`${label} refresh setup: missing try block`)
  const refreshSetupBody = refreshBody.slice(0, refreshTryIndex)
  assertMatch(
    refreshSetupBody,
    /const\s+representativeRequestRevision\s*=\s*representativeRevision\s*;/,
    `${label} refresh snapshots the representative revision before reading`,
  )
  assertMatch(refreshSetupBody, /pendingPageRetry\.value\s*=\s*null\s*;/, `${label} refresh clears the failed-page retry`)
  assertMatch(refreshSetupBody, /loadError\.value\s*=\s*['"]['"]\s*;/, `${label} refresh clears the old page error`)
  assertCompleteFunctionBody(
    refreshSetupBody,
    `
      const requestRevision = ++workListRevision;
      const requestedFilters = snapshotWorkFilters();
      const representativeRequestRevision = representativeRevision;
      pendingPageRetry.value = null;
      works.value = [];
      total.value = 0;
      page.value = 0;
      hasMore.value = true;
      loading.value = true;
      loadError.value = '';
    `,
    `${label} refresh pre-try setup has the complete request-state allowlist`,
  )

  const refreshTryBody = extractFunctionBlock(refreshBody, /\btry\b/, `${label} refresh success`)
  const refreshAwaitPattern = /const\s+\[result,\s*representatives\]\s*=\s*await\s+Promise\.all\(\s*\[\s*getActorWorks\(\s*\{\s*page:\s*1\s*,\s*size:\s*PAGE_SIZE\s*,\s*\.\.\.requestedFilters\s*\}\s*,\s*\{\s*showLoading:\s*false\s*,\s*showError:\s*false\s*,?\s*\}\s*,?\s*\)\s*,\s*getRepresentativeWorks\(\s*\{\s*showLoading:\s*false\s*,\s*showError:\s*false\s*,?\s*\}\s*\)\s*,?\s*\]\s*\)\s*;/
  const refreshAfterAwait = extractRemainderAfterSingleAwait(
    refreshTryBody,
    refreshAwaitPattern,
    `${label} refresh reads page one and representatives silently`,
  )
  const refreshSuccessGuardBody = extractOnlyTopLevelGuardBody(
    refreshAfterAwait,
    /^if\s*\(\s*isCurrentWorkListRequest\(requestRevision,\s*requestedFilters\)\s*\)/,
    `${label} refresh success`,
  )
  assertEqual(
    collectRefStateWrites(refreshSuccessGuardBody),
    ['works', 'total', 'representativeIds', 'page', 'hasMore', 'loadError'],
    `${label} refresh success has the exact protected state-write inventory`,
  )
  const representativeGuardBody = extractFunctionBlock(
    refreshSuccessGuardBody,
    /if\s*\(\s*representativeRequestRevision\s*===\s*representativeRevision\s*\)/,
    `${label} representative refresh guard`,
  )
  assertCompleteFunctionBody(
    representativeGuardBody,
    `representativeIds.value = representatives.map((item) => item.experienceId);`,
    `${label} representative refresh guard contains only the representative commit`,
  )
  assertPatternPrecedes(
    refreshSuccessGuardBody,
    /works\.value\s*=\s*result\.list\s*;/,
    /if\s*\(\s*representativeRequestRevision\s*===\s*representativeRevision\s*\)/,
    `${label} current list commits before the representative guard`,
  )
  assertPatternPrecedes(
    refreshSuccessGuardBody,
    /if\s*\(\s*representativeRequestRevision\s*===\s*representativeRevision\s*\)/,
    /page\.value\s*=\s*1\s*;/,
    `${label} current list commits continue after the representative guard`,
  )

  const refreshCatchBody = extractFunctionBlock(refreshBody, /catch\s*\(\s*error\s*\)/, `${label} refresh catch`)
  const refreshCatchGuardBody = extractOnlyTopLevelGuardBody(
    refreshCatchBody,
    /^if\s*\(\s*isCurrentWorkListRequest\(requestRevision,\s*requestedFilters\)\s*\)/,
    `${label} refresh catch`,
  )
  assertEqual(
    collectRefStateWrites(refreshCatchGuardBody),
    ['loadError'],
    `${label} refresh catch has the exact protected state-write inventory`,
  )

  const refreshFinallyBody = extractFunctionBlock(refreshBody, /\bfinally\b/, `${label} refresh finally`)
  const refreshFinallyGuardBody = extractOnlyTopLevelGuardBody(
    refreshFinallyBody,
    /^if\s*\(\s*isCurrentWorkListRequest\(requestRevision,\s*requestedFilters\)\s*\)/,
    `${label} refresh finally`,
  )
  assertEqual(
    collectRefStateWrites(refreshFinallyGuardBody),
    ['loading'],
    `${label} refresh finally has the exact protected state-write inventory`,
  )

  const loadNextBody = extractFunctionBlock(
    sections.script,
    /async\s+function\s+loadNextPage\s*\(\s*retryRequest\?:\s*PendingWorkPageRetry\s*\)\s*:\s*Promise<void>/,
    `${label} next page`,
  )
  assertMatch(loadNextBody, /const\s+requestRevision\s*=\s*retryRequest\?\.revision\s*\?\?\s*workListRevision\s*;/, `${label} snapshots the page revision`)
  assertMatch(loadNextBody, /const\s+requestedPage\s*=\s*retryRequest\?\.page\s*\?\?\s*page\.value\s*\+\s*1\s*;/, `${label} snapshots the target page`)
  assertMatch(loadNextBody, /const\s+requestedFilters\s*=\s*retryRequest\?\.filters\s*\?\?\s*snapshotWorkFilters\(\)\s*;/, `${label} snapshots page filters`)
  assertMatch(
    loadNextBody,
    /if\s*\(\s*\(loadError\.value\s*\|\|\s*pendingPageRetry\.value\)\s*&&\s*!retryRequest\s*\)\s*return\s*;/,
    `${label} suppresses automatic requests after an error`,
  )
  const currentPageEarlyReturn = /if\s*\(\s*!isCurrentWorkPageRequest\(requestRevision,\s*requestedPage,\s*requestedFilters\)\s*\)\s*return\s*;/
  assertPatternPrecedes(
    loadNextBody,
    currentPageEarlyReturn,
    /loading\.value\s*=\s*true/,
    `${label} validates the page snapshot before loading`,
  )

  const loadNextTryBody = extractFunctionBlock(loadNextBody, /\btry\b/, `${label} next-page success`)
  const loadNextAwaitPattern = /const\s+result\s*=\s*await\s+getActorWorks\(\s*\{\s*page:\s*requestedPage\s*,\s*size:\s*PAGE_SIZE\s*,\s*\.\.\.requestedFilters\s*\}\s*,\s*\{\s*showLoading:\s*false\s*,\s*showError:\s*false\s*,?\s*\}\s*,?\s*\)\s*;/
  const loadNextAfterAwait = extractRemainderAfterSingleAwait(
    loadNextTryBody,
    loadNextAwaitPattern,
    `${label} next page reads the snapped page silently`,
  )
  const loadNextSuccessGuardBody = extractOnlyTopLevelGuardBody(
    loadNextAfterAwait,
    /^if\s*\(\s*isCurrentWorkPageRequest\(requestRevision,\s*requestedPage,\s*requestedFilters\)\s*\)/,
    `${label} next-page success`,
  )
  assertEqual(
    collectRefStateWrites(loadNextSuccessGuardBody),
    ['works', 'total', 'page', 'hasMore', 'pendingPageRetry', 'loadError'],
    `${label} next-page success has the exact protected state-write inventory`,
  )
  assertMatch(
    loadNextSuccessGuardBody,
    /works\.value\s*=\s*\[\s*\.\.\.works\.value\s*,\s*\.\.\.result\.list\s*\]\s*;/,
    `${label} appends a successful next page`,
  )
  assertMatch(loadNextSuccessGuardBody, /page\.value\s*=\s*requestedPage\s*;/, `${label} advances only to the requested page`)
  assertMatch(loadNextSuccessGuardBody, /pendingPageRetry\.value\s*=\s*null\s*;/, `${label} clears the failed page after success`)
  assertMatch(loadNextSuccessGuardBody, /loadError\.value\s*=\s*['"]['"]\s*;/, `${label} clears the page error after success`)

  const loadNextCatchBody = extractFunctionBlock(loadNextBody, /catch\s*\(\s*error\s*\)/, `${label} next-page catch`)
  const loadNextCatchGuardBody = extractOnlyTopLevelGuardBody(
    loadNextCatchBody,
    /^if\s*\(\s*isCurrentWorkPageRequest\(requestRevision,\s*requestedPage,\s*requestedFilters\)\s*\)/,
    `${label} next-page catch`,
  )
  assertEqual(
    collectRefStateWrites(loadNextCatchGuardBody),
    ['loadError', 'pendingPageRetry'],
    `${label} next-page catch has the exact protected state-write inventory`,
  )
  assertNoMatch(
    loadNextCatchGuardBody,
    /\b(?:works|page|total|hasMore|representativeIds|loading)\.value\s*(?:=|\+=|-=|\+\+|--)/,
    `${label} page failure cannot overwrite list or loading state`,
  )
  assertMatch(
    loadNextCatchGuardBody,
    /pendingPageRetry\.value\s*=\s*\{\s*revision:\s*requestRevision\s*,\s*page:\s*requestedPage\s*,\s*filters:\s*requestedFilters\s*,?\s*\}\s*;/,
    `${label} records the failed page snapshot for retry`,
  )

  const loadNextFinallyBody = extractFunctionBlock(loadNextBody, /\bfinally\b/, `${label} next-page finally`)
  const loadNextFinallyGuardBody = extractOnlyTopLevelGuardBody(
    loadNextFinallyBody,
    /^if\s*\(\s*isCurrentWorkListRequest\(requestRevision,\s*requestedFilters\)\s*\)/,
    `${label} next-page finally`,
  )
  assertEqual(
    collectRefStateWrites(loadNextFinallyGuardBody),
    ['loading'],
    `${label} next-page finally has the exact protected state-write inventory`,
  )

  const retryBody = extractFunctionBlock(
    sections.script,
    /function\s+retryWorkList\s*\(\s*\)\s*:\s*void/,
    `${label} retry command`,
  )
  assertMatch(
    retryBody,
    /^\s*if\s*\(\s*loading\.value\s*\)\s*return\s*;/,
    `${label} retry loading guard is the first executable statement`,
  )
  assertCompleteFunctionBody(
    retryBody,
    `
      if (loading.value) return;
      const retryRequest = pendingPageRetry.value;
      if (retryRequest) {
        void loadNextPage(retryRequest);
        return;
      }
      void refreshWorks();
    `,
    `${label} retry command has the complete request-preserving allowlist`,
  )

  const saveRepresentativeBody = extractFunctionBlock(
    sections.script,
    /async\s+function\s+saveRepresentativeSelection\s*\(\s*\)\s*:\s*Promise<void>/,
    `${label} representative save`,
  )
  assertNoMatch(
    saveRepresentativeBody,
    /if\s*\(\s*savingRepresentatives\.value\s*\)\s*return\s*;/,
    `${label} representative save does not add a duplicate-submit gate`,
  )
  const saveRepresentativeTryBody = extractFunctionBlock(
    saveRepresentativeBody,
    /\btry\b/,
    `${label} representative save success`,
  )
  assertMatch(
    saveRepresentativeTryBody,
    /const\s+saved\s*=\s*await\s+setRepresentativeWorks\(selectedRepresentativeIds\.value\)\s*;\s*representativeRevision\s*\+=\s*1\s*;\s*representativeIds\.value\s*=\s*saved\.map\(\(item\)\s*=>\s*item\.experienceId\)\s*;/,
    `${label} successful representative save invalidates older reads before committing`,
  )
  assertEqual(
    (sections.script.match(/\brepresentativeRevision\s*\+=\s*1\s*;/g) || []).length,
    1,
    `${label} representative revision advances only after a successful save`,
  )

  assertEqual(
    (sections.script.match(/\bgetActorWorks\s*\(/g) || []).length,
    2,
    `${label} has exactly two paged work reads`,
  )
  assertEqual(
    (sections.script.match(/\bgetRepresentativeWorks\s*\(/g) || []).length,
    1,
    `${label} has exactly one representative read`,
  )

  const reachBottomBody = extractFunctionBlock(
    sections.script,
    /onReachBottom\(\s*\(\)\s*=>/,
    `${label} reach-bottom trigger`,
  )
  assertMatch(
    reachBottomBody,
    /if\s*\(\s*loadError\.value\s*\|\|\s*pendingPageRetry\.value\s*\)\s*return\s*;/,
    `${label} blocks reach-bottom retries while an error is pending`,
  )
  assertMatch(reachBottomBody, /loadNextPage\(\)/, `${label} keeps normal reach-bottom pagination`)
}

assertWorkListRequestRecovery(worksPage, 'Work library request recovery')

assertMutationTurnsGateRed(
  worksPage,
  /v-model="keywordInput"/,
  'v-model="filters.keyword"',
  assertWorkListRequestRecovery,
  'work list search input applied-filter rebind',
  { requireUnique: true, expectedFailurePattern: /binds an independent keyword draft and commits it on confirm/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /let\s+workListRevision\s*=\s*0\s*;/,
  'let staleWorkListRevision = 0;',
  assertWorkListRequestRecovery,
  'work list revision removal',
  { requireUnique: true, expectedFailurePattern: /declares a monotonic request revision/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /let\s+representativeRevision\s*=\s*0\s*;/,
  'let staleRepresentativeRevision = 0;',
  assertWorkListRequestRecovery,
  'work list representative revision removal',
  { requireUnique: true, expectedFailurePattern: /declares a representative request revision/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /keyword:\s*filters\.keyword\s*,/,
  "keyword: '',",
  assertWorkListRequestRecovery,
  'work list keyword snapshot removal',
  { requireUnique: true, expectedFailurePattern: /snapshots keyword/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /publishStatus:\s*filters\.publishStatus\s*,/,
  "publishStatus: '',",
  assertWorkListRequestRecovery,
  'work list publish-status snapshot removal',
  { requireUnique: true, expectedFailurePattern: /snapshots publish status/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /workTypeCode:\s*filters\.workTypeCode\s*,/,
  "workTypeCode: '',",
  assertWorkListRequestRecovery,
  'work list work-type snapshot removal',
  { requireUnique: true, expectedFailurePattern: /snapshots work type/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /filters\.keyword\s*===\s*snapshot\.keyword/,
  'true',
  assertWorkListRequestRecovery,
  'work list keyword current-filter comparison removal',
  { requireUnique: true, expectedFailurePattern: /filter predicate has the complete three-field allowlist/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /filters\.publishStatus\s*===\s*snapshot\.publishStatus/,
  'true',
  assertWorkListRequestRecovery,
  'work list publish-status current-filter comparison removal',
  { requireUnique: true, expectedFailurePattern: /filter predicate has the complete three-field allowlist/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /filters\.workTypeCode\s*===\s*snapshot\.workTypeCode/,
  'true',
  assertWorkListRequestRecovery,
  'work list work-type current-filter comparison removal',
  { requireUnique: true, expectedFailurePattern: /filter predicate has the complete three-field allowlist/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /filters\.workTypeCode\s*===\s*snapshot\.workTypeCode\s*;/,
  'filters.workTypeCode === snapshot.workTypeCode || true;',
  assertWorkListRequestRecovery,
  'work list filter predicate unconditional allowance injection',
  { requireUnique: true, expectedFailurePattern: /filter predicate has the complete three-field allowlist/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /requestRevision\s*===\s*workListRevision\s*&&\s*filtersMatch\(requestedFilters\)/,
  'filtersMatch(requestedFilters)',
  assertWorkListRequestRecovery,
  'work list current-revision guard removal',
  { requireUnique: true, expectedFailurePattern: /current-list predicate has the complete revision-and-filter allowlist/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /requestRevision\s*===\s*workListRevision\s*&&\s*filtersMatch\(requestedFilters\)/,
  'requestRevision === workListRevision',
  assertWorkListRequestRecovery,
  'work list current-filter guard removal',
  { requireUnique: true, expectedFailurePattern: /current-list predicate has the complete revision-and-filter allowlist/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /return\s+requestRevision\s*===\s*workListRevision\s*&&\s*filtersMatch\(requestedFilters\)\s*;/,
  'return requestRevision === workListRevision && filtersMatch(requestedFilters) || true;',
  assertWorkListRequestRecovery,
  'work list current-list predicate unconditional allowance injection',
  { requireUnique: true, expectedFailurePattern: /current-list predicate has the complete revision-and-filter allowlist/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /const\s+requestRevision\s*=\s*\+\+workListRevision\s*;/,
  'const requestRevision = workListRevision;',
  assertWorkListRequestRecovery,
  'work list refresh revision increment removal',
  { requireUnique: true, expectedFailurePattern: /refresh increments revision before state changes/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(async\s+function\s+refreshWorks\s*\(\s*\)\s*:\s*Promise<void>\s*\{)/,
  '$1\n  if (loading.value) return;',
  assertWorkListRequestRecovery,
  'work list refresh loading blockade injection',
  { requireUnique: true, expectedFailurePattern: /refresh never waits for an older loading flag/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /const\s+representativeRequestRevision\s*=\s*representativeRevision\s*;/,
  '',
  assertWorkListRequestRecovery,
  'work list representative revision snapshot removal',
  { requireUnique: true, expectedFailurePattern: /refresh snapshots the representative revision before reading/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(const\s+representativeRequestRevision\s*=\s*representativeRevision\s*;)\s*pendingPageRetry\.value\s*=\s*null\s*;/,
  '$1',
  assertWorkListRequestRecovery,
  'work list refresh failed-page retry clearing removal',
  { requireUnique: true, expectedFailurePattern: /refresh clears the failed-page retry/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(loading\.value\s*=\s*true\s*;)\s*loadError\.value\s*=\s*['"]['"]\s*;(\s*try\s*\{)/,
  '$1$2',
  assertWorkListRequestRecovery,
  'work list refresh error clearing removal',
  { requireUnique: true, expectedFailurePattern: /refresh clears the old page error/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(getActorWorks\(\s*\{\s*page:\s*1\s*,\s*size:\s*PAGE_SIZE\s*,\s*\.\.\.requestedFilters\s*\}\s*,\s*\{\s*)showLoading:\s*false\s*,/,
  '$1',
  assertWorkListRequestRecovery,
  'work list refresh page-one loading suppression removal',
  { requireUnique: true, expectedFailurePattern: /refresh reads page one and representatives silently/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(getActorWorks\(\s*\{\s*page:\s*1\s*,\s*size:\s*PAGE_SIZE\s*,\s*\.\.\.requestedFilters\s*\}\s*,\s*\{\s*showLoading:\s*false\s*,\s*)showError:\s*false\s*,?/,
  '$1',
  assertWorkListRequestRecovery,
  'work list refresh page-one error suppression removal',
  { requireUnique: true, expectedFailurePattern: /refresh reads page one and representatives silently/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(getRepresentativeWorks\(\s*\{\s*)showLoading:\s*false\s*,/,
  '$1',
  assertWorkListRequestRecovery,
  'work list representative loading suppression removal',
  { requireUnique: true, expectedFailurePattern: /refresh reads page one and representatives silently/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(getRepresentativeWorks\(\s*\{\s*showLoading:\s*false\s*,\s*)showError:\s*false\s*,?/,
  '$1',
  assertWorkListRequestRecovery,
  'work list representative error suppression removal',
  { requireUnique: true, expectedFailurePattern: /refresh reads page one and representatives silently/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(\]\s*\)\s*;)\s*if\s*\(\s*isCurrentWorkListRequest\(requestRevision,\s*requestedFilters\)\s*\)/,
  '$1\n    if (true)',
  assertWorkListRequestRecovery,
  'work list refresh success guard removal',
  { requireUnique: true, expectedFailurePattern: /refresh success: current guard must be the only top-level statement/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(\]\s*\)\s*;)\s*(if\s*\(\s*isCurrentWorkListRequest\(requestRevision,\s*requestedFilters\)\s*\))/,
  '$1\n    total.value = result.total;\n    $2',
  assertWorkListRequestRecovery,
  'work list refresh pre-guard state write injection',
  { requireUnique: true, expectedFailurePattern: /refresh success: current guard must be the only top-level statement/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(\]\s*\)\s*;\s*)(if\s*\(\s*isCurrentWorkListRequest\(requestRevision,\s*requestedFilters\)\s*\)\s*\{[\s\S]*?loadError\.value\s*=\s*['"]['"]\s*;\s*\})/,
  '$1if (false) {\n    $2\n    }',
  assertWorkListRequestRecovery,
  'work list refresh current guard outer-false wrapping injection',
  { requireUnique: true, expectedFailurePattern: /refresh success: current guard must be the only top-level statement/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /if\s*\(\s*representativeRequestRevision\s*===\s*representativeRevision\s*\)/,
  'if (true)',
  assertWorkListRequestRecovery,
  'work list representative refresh guard removal',
  { requireUnique: true, expectedFailurePattern: /representative refresh guard/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(catch\s*\(\s*error\s*\)\s*\{)\s*if\s*\(\s*isCurrentWorkListRequest\(requestRevision,\s*requestedFilters\)\s*\)/,
  '$1\n    if (true)',
  assertWorkListRequestRecovery,
  'work list refresh catch guard removal',
  { requireUnique: true, expectedFailurePattern: /refresh catch: current guard must be the only top-level statement/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(async\s+function\s+refreshWorks[\s\S]*?finally\s*\{\s*if\s*\()isCurrentWorkListRequest\(requestRevision,\s*requestedFilters\)(\)\s*\{)/,
  '$1true$2',
  assertWorkListRequestRecovery,
  'work list refresh finally guard removal',
  { requireUnique: true, expectedFailurePattern: /refresh finally: current guard must be the only top-level statement/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /requestedPage\s*===\s*page\.value\s*\+\s*1\s*;/,
  'requestedPage > 0;',
  assertWorkListRequestRecovery,
  'work list expected-next-page guard removal',
  { requireUnique: true, expectedFailurePattern: /current-page predicate has the complete list-and-next-page allowlist/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /return\s+isCurrentWorkListRequest\(requestRevision,\s*requestedFilters\)\s*&&\s*requestedPage\s*===\s*page\.value\s*\+\s*1\s*;/,
  'return isCurrentWorkListRequest(requestRevision, requestedFilters) && requestedPage === page.value + 1 || true;',
  assertWorkListRequestRecovery,
  'work list current-page predicate unconditional allowance injection',
  { requireUnique: true, expectedFailurePattern: /current-page predicate has the complete list-and-next-page allowlist/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(getActorWorks\(\s*\{\s*page:\s*requestedPage\s*,\s*size:\s*PAGE_SIZE\s*,\s*\.\.\.requestedFilters\s*\}\s*,\s*\{\s*)showLoading:\s*false\s*,/,
  '$1',
  assertWorkListRequestRecovery,
  'work list next-page loading suppression removal',
  { requireUnique: true, expectedFailurePattern: /next page reads the snapped page silently/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(getActorWorks\(\s*\{\s*page:\s*requestedPage\s*,\s*size:\s*PAGE_SIZE\s*,\s*\.\.\.requestedFilters\s*\}\s*,\s*\{\s*showLoading:\s*false\s*,\s*)showError:\s*false\s*,?/,
  '$1',
  assertWorkListRequestRecovery,
  'work list next-page error suppression removal',
  { requireUnique: true, expectedFailurePattern: /next page reads the snapped page silently/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(const\s+result\s*=\s*await\s+getActorWorks\([\s\S]*?\)\s*;)\s*if\s*\(\s*isCurrentWorkPageRequest\(requestRevision,\s*requestedPage,\s*requestedFilters\)\s*\)/,
  '$1\n    if (true)',
  assertWorkListRequestRecovery,
  'work list page success guard removal',
  { requireUnique: true, expectedFailurePattern: /next-page success: current guard must be the only top-level statement/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(const\s+result\s*=\s*await\s+getActorWorks\([\s\S]*?\)\s*;)\s*(if\s*\(\s*isCurrentWorkPageRequest\(requestRevision,\s*requestedPage,\s*requestedFilters\)\s*\))/,
  '$1\n    total.value = result.total;\n    $2',
  assertWorkListRequestRecovery,
  'work list page pre-guard state write injection',
  { requireUnique: true, expectedFailurePattern: /next-page success: current guard must be the only top-level statement/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(if\s*\(\s*isCurrentWorkPageRequest\(requestRevision,\s*requestedPage,\s*requestedFilters\)\s*\)\s*\{[\s\S]*?pendingPageRetry\.value\s*=\s*null\s*;\s*loadError\.value\s*=\s*['"]['"]\s*;\s*\})/,
  'if (false) {\n    $1\n    }',
  assertWorkListRequestRecovery,
  'work list page current guard outer-false wrapping injection',
  { requireUnique: true, expectedFailurePattern: /next-page success: current guard must be the only top-level statement/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(catch\s*\(\s*error\s*\)\s*\{)\s*if\s*\(\s*isCurrentWorkPageRequest\(requestRevision,\s*requestedPage,\s*requestedFilters\)\s*\)/,
  '$1\n    if (true)',
  assertWorkListRequestRecovery,
  'work list page catch guard removal',
  { requireUnique: true, expectedFailurePattern: /next-page catch: current guard must be the only top-level statement/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(catch\s*\(\s*error\s*\)\s*\{\s*if\s*\(\s*isCurrentWorkPageRequest\(requestRevision,\s*requestedPage,\s*requestedFilters\)\s*\)\s*\{)/,
  '$1\n      works.value = [];',
  assertWorkListRequestRecovery,
  'work list page failure list clearing injection',
  { requireUnique: true, expectedFailurePattern: /next-page catch has the exact protected state-write inventory/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /filters:\s*requestedFilters\s*,/,
  'filters: snapshotWorkFilters(),',
  assertWorkListRequestRecovery,
  'work list failed-page snapshot replacement',
  { requireUnique: true, expectedFailurePattern: /records the failed page snapshot for retry/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(pendingPageRetry\.value\s*=\s*null\s*;)\s*loadError\.value\s*=\s*['"]['"]\s*;/,
  '$1',
  assertWorkListRequestRecovery,
  'work list successful-page error clearing removal',
  { requireUnique: true, expectedFailurePattern: /next-page success has the exact protected state-write inventory/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(async\s+function\s+loadNextPage[\s\S]*?finally\s*\{\s*if\s*\()isCurrentWorkListRequest\(requestRevision,\s*requestedFilters\)(\)\s*\{)/,
  '$1true$2',
  assertWorkListRequestRecovery,
  'work list page finally guard removal',
  { requireUnique: true, expectedFailurePattern: /next-page finally: current guard must be the only top-level statement/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /void\s+loadNextPage\(retryRequest\)\s*;/,
  'void refreshWorks();',
  assertWorkListRequestRecovery,
  'work list same-page retry replacement',
  { requireUnique: true, expectedFailurePattern: /retry command has the complete request-preserving allowlist/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(function\s+changePublishStatus[\s\S]*?filters\.publishStatus\s*=[^;]+;)\s*(?:void\s+)?refreshWorks\(\)\s*;/,
  '$1 applyFilters();',
  assertWorkListRequestRecovery,
  'work list publish-status picker search-submit injection',
  { requireUnique: true, expectedFailurePattern: /publish-status picker has the complete status-only allowlist/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(function\s+changeWorkType[\s\S]*?filters\.workTypeCode\s*=[^;]+;)\s*(?:void\s+)?refreshWorks\(\)\s*;/,
  '$1 applyFilters();',
  assertWorkListRequestRecovery,
  'work list work-type picker search-submit injection',
  { requireUnique: true, expectedFailurePattern: /work-type picker has the complete type-only allowlist/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(onReachBottom\(\s*\(\)\s*=>\s*\{)\s*if\s*\(\s*loadError\.value\s*\|\|\s*pendingPageRetry\.value\s*\)\s*return\s*;/,
  '$1',
  assertWorkListRequestRecovery,
  'work list reach-bottom error suppression removal',
  { requireUnique: true, expectedFailurePattern: /blocks reach-bottom retries while an error is pending/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(async\s+function\s+refreshWorks\s*\(\s*\)\s*:\s*Promise<void>\s*\{\s*const\s+requestRevision\s*=\s*\+\+workListRevision\s*;)/,
  `function commitKeywordDraft(): void {
  filters.keyword = keywordInput.value;
}

$1
  commitKeywordDraft();`,
  assertWorkListRequestRecovery,
  'work list refresh indirect keyword draft commit injection',
  { requireUnique: true, expectedFailurePattern: /refresh pre-try setup has the complete request-state allowlist/ },
)
assertMutationTurnsGateRed(
  worksPage,
  /(function\s+snapshotWorkFilters\s*\(\s*\)\s*:\s*WorkFilterSnapshot\s*\{\s*)return\s+\{/,
  `function commitKeywordDraft(): void {
  filters.keyword = keywordInput.value;
}

$1commitKeywordDraft();
  return {`,
  assertWorkListRequestRecovery,
  'work list snapshot indirect keyword draft commit injection',
  { requireUnique: true, expectedFailurePattern: /filter snapshot has the complete side-effect-free allowlist/ },
)
assertEqual(
  functionScopedMutationCount - workRequestStateMutationStartCount,
  48,
  'Work request-state fixed mutation inventory',
)
function assertWorkLibraryNeutralShell(source, label) {
  const sections = extractSfcSections(source, `${label} SFC`)
  assertNeutralProfilePackageShell(source, sections, 'works-page', label, {
    groupSelectors: [
      /\.works-page__summary-row\s*/,
      /\.works-page__filters\s*/,
      /\.works-page__toolbar\s*/,
      /\.works-page__list\s*/,
      /\.works-page__error\s*/,
    ],
    primaryActionSelectors: [/\.works-page__add\s*/, /\.works-page__save\s*/],
    buttonSelectors: [/\.works-page__add\s*/, /\.works-page__toolbar-button\s*/, /\.works-page__error\s+button\s*/, /\.works-page__save\s*/],
  })
  assertMatch(
    sections.template,
    /:class="\{\s*'works-page--representative':\s*representativeMode\s*\}"/,
    `${label} enables footer clearance only in representative mode`,
  )
  assertStyleBlock(
    sections.style,
    /\.works-page--representative\s*/,
    /padding-bottom:\s*calc\(138rpx\s*\+\s*env\(safe-area-inset-bottom\)\)\s*;/,
    `${label} reserves the fixed representative footer plus group spacing`,
  )
  assertStyleBlock(sections.style, /\.works-page__footer\s*/, /position:\s*fixed\s*;/, `${label} keeps a fixed representative footer`)
  assertStyleBlock(sections.style, /\.works-page__footer\s*/, /bottom:\s*0\s*;/, `${label} pins the representative footer to the viewport bottom`)
  assertStyleBlock(
    sections.style,
    /\.works-page__footer\s*/,
    /padding:\s*14rpx\s+\$kp-spacing-page\s+calc\(14rpx\s*\+\s*env\(safe-area-inset-bottom\)\)\s*;/,
    `${label} representative footer reserves the bottom safe area`,
  )
}
assertWorkLibraryNeutralShell(worksPage, 'Work library')

const actorWorkTypes = await readText('kaipai-frontend/src/types/actor-work.ts')
const actorWorkSaveBody = extractFunctionBlock(
  actorWorkTypes,
  /export\s+interface\s+ActorWorkSave/,
  'ActorWorkSave',
)
assertNoMatch(actorWorkSaveBody, /\bsourceType\??\s*:/, 'Work save DTO excludes server provenance')
assertMatch(
  actorWorkTypes,
  /export\s+type\s+ActorWorkSourceType\s*=\s*'manual'\s*\|\s*'import'\s*\|\s*'migration'/,
  'Work provenance values',
)
assertNoMatch(
  actorWorkTypes,
  /ActorWorkSourceType[^\n]*(?:explicit|inferred_from_roles|direct)/,
  'Work provenance excludes import evidence values',
)
const actorWorkBody = extractFunctionBlock(
  actorWorkTypes,
  /export\s+interface\s+ActorWork\b(?:\s+extends[^\{]+)?/,
  'ActorWork',
)
assertMatch(actorWorkBody, /\bsourceType:\s*ActorWorkSourceType\s*;/, 'Work response includes provenance')
assertNoMatch(actorWorkTypes, /\bPositiveSortNo\b/, 'Work asset sort uses the API number contract')
const actorAssetBindingBody = extractFunctionBlock(
  actorWorkTypes,
  /export\s+interface\s+ActorAssetBinding/,
  'ActorAssetBinding',
)
assertMatch(actorAssetBindingBody, /\bassetId:\s*number\s*;/, 'Work asset binding ID')
assertMatch(actorAssetBindingBody, /\busageCode:\s*'still'\s*\|\s*'clip'\s*;/, 'Work asset binding usage')
assertMatch(actorAssetBindingBody, /\bsortNo:\s*number\s*;/, 'Work asset binding numeric sort')
assertEqual(
  [...actorAssetBindingBody.matchAll(/^\s*(\w+)\s*:/gm)].map((match) => match[1]),
  ['assetId', 'usageCode', 'sortNo'],
  'Work asset binding has exactly three fields',
)
const actorWorkAssetBody = extractFunctionBlock(
  actorWorkTypes,
  /export\s+interface\s+ActorWorkAsset\s+extends\s+ActorAssetBinding/,
  'ActorWorkAsset',
)
assertMatch(actorWorkAssetBody, /\bmediaType:\s*'photo'\s*\|\s*'video'\s*;/, 'Work asset snapshot media type')
assertMatch(actorWorkAssetBody, /\bcategoryCode:\s*string\s*\|\s*null\s*;/, 'Work asset nullable category')
assertMatch(actorWorkAssetBody, /\boriginalName:\s*string\s*\|\s*null\s*;/, 'Work asset nullable name')
assertMatch(actorWorkAssetBody, /\bprocessStatus:\s*ActorAssetProcessStatus\s*;/, 'Work asset process status')
assertEqual(
  [...actorWorkAssetBody.matchAll(/^\s*(\w+)\s*:/gm)].map((match) => match[1]),
  ['mediaType', 'categoryCode', 'originalName', 'processStatus'],
  'Work asset snapshot has exactly four metadata fields beyond its three bindings',
)
assertNoMatch(
  actorWorkAssetBody,
  /\b(?:accessUrl|storage|bucket|objectKey|storageProvider)\b/,
  'Work asset snapshot excludes access and storage location fields',
)

assertMatch(
  actorWorkApi,
  /export\s+function\s+getActorWorkAssets\s*\(\s*id:\s*number\s*\)\s*:\s*Promise<ActorWorkAsset\[\]>\s*\{\s*return\s+get\(\s*`\/api\/actor\/works\/\$\{id\}\/assets`\s*\)\s*;?\s*\}/,
  'Work asset complete snapshot API',
)
const replaceActorWorkAssetsBody = extractFunctionBlock(
  actorWorkApi,
  /export\s+function\s+replaceActorWorkAssets\s*\(\s*id:\s*number,\s*bindings:\s*ActorAssetBinding\[\]\s*\)\s*:\s*Promise<void>/,
  'replaceActorWorkAssets',
)
assertMatch(
  replaceActorWorkAssetsBody,
  /return\s+put<void>\(\s*`\/api\/actor\/works\/\$\{id\}\/assets`,\s*\{\s*bindings\s*\}\s*\)/,
  'Work asset complete-set replacement API',
)

const assetSelectionStore = await readText('kaipai-frontend/src/stores/asset-selection.ts')
const selectedAssetBody = extractFunctionBlock(
  assetSelectionStore,
  /interface\s+SelectedAsset/,
  'SelectedAsset',
)
assertEqual(
  [...selectedAssetBody.matchAll(/^\s*(\w+)\??\s*:/gm)].map((match) => match[1]),
  ['assetId'],
  'Avatar route selection stores exactly one asset ID',
)
assertNoMatch(assetSelectionStore, /previewUrl|accessUrl/, 'Selection store excludes short-lived access URLs')
assertMatch(assetSelectionStore, /workSelection\s*=\s*ref<ActorWorkAsset\[\]\s*\|\s*null>/, 'In-memory complete work selection')
function assertSetWorkSelectionContract(source, label) {
  const body = extractFunctionBlock(
    source,
    /function\s+setWorkSelection\s*\(\s*assets:\s*ActorWorkAsset\[\]\s*\)\s*:\s*void/,
    label,
  )
  assertMatch(body, /workSelection\.value\s*=\s*assets\.map\(\s*\(?asset\)?\s*=>\s*\(\s*\{\s*\.\.\.asset\s*\}\s*\)\s*\)/, `${label} clones on write`)
  assertNoMatch(body, /workSelection\.value\s*=\s*assets\s*;/, `${label} never retains the caller array`)
}
function assertConsumeWorkSelectionContract(source, label) {
  const body = extractFunctionBlock(
    source,
    /function\s+consumeWorkSelection\s*\(\s*\)\s*:\s*ActorWorkAsset\[\]\s*\|\s*null/,
    label,
  )
  assertMatch(body, /workSelection\.value\?\.map\(\s*\(?asset\)?\s*=>\s*\(\s*\{\s*\.\.\.asset\s*\}\s*\)\s*\)/, `${label} clones on read`)
  assertMatch(body, /workSelection\.value\s*=\s*null/, `${label} clears the one-shot value`)
  assertMatch(body, /return\s+selected/, `${label} returns the detached selection`)
}
assertSetWorkSelectionContract(assetSelectionStore, 'setWorkSelection')
assertConsumeWorkSelectionContract(assetSelectionStore, 'consumeWorkSelection')
assertMatch(assetSelectionStore, /function\s+clearWorkSelection\s*\(/, 'Clear work selection')
assertNoMatch(assetSelectionStore, /localStorage|uni\.(?:set|remove|clear)Storage|persist\s*:/, 'Work selection is not persisted')
assertMatch(assetSelectionStore, /selectAvatar[\s\S]*consumeAvatar/, 'Avatar selection remains supported')
assertMatch(assetSelectionStore, /avatarSelection\.value\s*=\s*\{\s*\.\.\.asset\s*\}/, 'Avatar selection is cloned on write')
assertMutationTurnsGateRed(
  assetSelectionStore,
  /workSelection\.value\s*=\s*assets\.map\(\s*\(?asset\)?\s*=>\s*\(\s*\{\s*\.\.\.asset\s*\}\s*\)\s*\)\s*;?/,
  'workSelection.value = assets;',
  assertSetWorkSelectionContract,
  'setWorkSelection clone-on-write removal',
)
assertMutationTurnsGateRed(
  assetSelectionStore,
  /workSelection\.value\s*=\s*null\s*;/,
  '',
  assertConsumeWorkSelectionContract,
  'consumeWorkSelection one-shot clear removal',
)

const workEditPage = await readText('kaipai-frontend/src/pkg-profile/work-edit/index.vue')
const workEditSections = extractSfcSections(workEditPage, 'Work editor SFC')
assertMatch(workEditPage, /getActorWork[\s\S]*updateActorWork[\s\S]*createActorWork/, 'Work create and edit')
assertMatch(workEditPage, /项目名称[\s\S]*角色名称[\s\S]*播出状态[\s\S]*作品类型[\s\S]*拍摄时间[\s\S]*平台/, 'Complete work form')
assertNoMatch(workEditPage, /:\s*any\b|as any\b/, 'Typed work editor')
assertMatch(
  workEditSections.template,
  /work-edit__source-row[\s\S]*作品来源[\s\S]*\{\{\s*sourceTypeLabel\s*\}\}/,
  'Existing work provenance is a compact read-only row',
)
assertMatch(
  workEditSections.script,
  /manual:\s*'手动创建'[\s\S]*import:\s*'智能导入'[\s\S]*migration:\s*'历史迁移'/,
  'Work provenance display labels',
)
assertNoMatch(
  workEditSections.script,
  /reactive<ActorWorkSave>\s*\(\s*\{[^}]*\bsourceType\s*:/,
  'Work draft excludes provenance',
)
const hydrateWorkBody = extractFunctionBlock(
  workEditSections.script,
  /async\s+function\s+hydrateWork\s*\([^)]*\)/,
  'hydrateWork',
)
assertMatch(hydrateWorkBody, /workSourceType\.value\s*=\s*work\.sourceType/, 'Hydrated provenance stays read-only')
assertNoMatch(hydrateWorkBody, /Object\.assign\(draft,\s*work\)|sourceType\s*:/, 'Hydration excludes provenance from draft')
assertMatch(workEditSections.script, /type\s+DetailState\s*=\s*'loading'\s*\|\s*'error'\s*\|\s*'ready'/, 'Work detail has explicit loading error ready states')
assertMatch(workEditSections.script, /detailState\s*=\s*ref<DetailState>\(\s*'loading'\s*\)/, 'Existing work detail starts fail-closed')
assertMatch(hydrateWorkBody, /detailState\.value\s*=\s*'loading'[\s\S]*detailState\.value\s*=\s*'ready'[\s\S]*catch[\s\S]*detailState\.value\s*=\s*'error'/, 'Work detail hydration owns all three states')
assertMatch(workEditSections.script, /let\s+detailRequestRevision\s*=\s*0/, 'Work detail requests have an independent revision')
assertMatch(hydrateWorkBody, /const\s+requestRevision\s*=\s*\+\+detailRequestRevision[\s\S]*await\s+getActorWork/, 'Work detail increments its request revision before loading')
assertEqual(
  [...hydrateWorkBody.matchAll(/requestRevision\s*!==\s*detailRequestRevision/g)].length,
  2,
  'Only the latest work detail request can commit success or failure state',
)
assertMatch(
  hydrateWorkBody,
  /await\s+getActorWork[\s\S]*if\s*\(\s*requestRevision\s*!==\s*detailRequestRevision\s*\)\s*return[\s\S]*detailState\.value\s*=\s*'ready'[\s\S]*catch[\s\S]*if\s*\(\s*requestRevision\s*!==\s*detailRequestRevision\s*\)\s*return[\s\S]*detailState\.value\s*=\s*'error'/,
  'Stale work detail requests return before writing ready or error state',
)
const retryWorkDetailBody = extractFunctionBlock(
  workEditSections.script,
  /async\s+function\s+retryWorkDetail\s*\([^)]*\)/,
  'retryWorkDetail',
)
assertMatch(retryWorkDetailBody, /detailState\.value\s*===\s*'loading'[\s\S]*return/, 'Work detail retry is disabled while a request is loading')
assertMatch(retryWorkDetailBody, /hydrateWork\(workId\.value\)/, 'Failed work detail exposes a retry')
assertMatch(workEditSections.template, /detailState\s*===\s*'error'[\s\S]*retryWorkDetail[\s\S]*重新加载/, 'Work detail error is rendered with retry')
assertMatch(workEditSections.script, /editorReady\s*=\s*computed\(\(\)\s*=>\s*detailState\.value\s*===\s*'ready'\s*&&\s*assetSnapshotState\.value\s*===\s*'ready'\)/, 'Editor requires both complete snapshots')
assertMatch(workEditSections.template, /<view\s+class="work-edit__footer">\s*<button\s+:disabled="[^\"]*!editorReady[^\"]*"/, 'Footer save button is disabled until both snapshots are ready')
const buildWorkSavePayloadBody = extractFunctionBlock(
  workEditSections.script,
  /function\s+buildWorkSavePayload\s*\(\s*\)\s*:\s*ActorWorkSave/,
  'buildWorkSavePayload',
)
assertNoMatch(buildWorkSavePayloadBody, /sourceType/, 'Work save payload excludes provenance')
const toBindingsBody = extractFunctionBlock(
  workEditSections.script,
  /function\s+toBindings\s*\(\s*assets:\s*ActorWorkAsset\[\]\s*\)\s*:\s*ActorAssetBinding\[\]/,
  'toBindings',
)
assertMatch(toBindingsBody, /return\s+assets\.map\(/, 'Binding payload maps the complete target collection including empty arrays')
assertNoMatch(toBindingsBody, /\bif\b|\.filter\(|\.length\b/, 'Empty complete target collection is not suppressed')
const saveWorkBody = extractFunctionBlock(
  workEditSections.script,
  /async\s+function\s+saveWork\s*\(\s*\)/,
  'saveWork',
)
assertMatch(saveWorkBody, /const\s+payload\s*=\s*buildWorkSavePayload\(\)/, 'Work save uses an explicit payload')
assertMatch(saveWorkBody, /updateActorWork\(workId\.value,\s*payload\)[\s\S]*createActorWork\(payload\)/, 'Work save submits only editable fields')
assertMatch(saveWorkBody, /if\s*\(\s*!editorReady\.value\s*\)[\s\S]{0,180}return/, 'Work save fails closed until both snapshots are ready')
assertMatch(workEditSections.script, /textEditingLocked\s*=\s*computed\([\s\S]{0,180}!editorReady\.value/, 'Text editing fails closed until both snapshots are ready')
assertMatch(workEditSections.script, /assetEditingLocked\s*=\s*computed\([\s\S]{0,180}!editorReady\.value/, 'Asset editing fails closed until both snapshots are ready')
assertMatch(
  workEditSections.script,
  /else\s*\{\s*detailState\.value\s*=\s*'ready'[\s\S]{0,240}assetSnapshotState\.value\s*=\s*'ready'/,
  'New work explicitly starts with ready empty snapshots',
)
assertMatch(workEditSections.script, /getActorWorkAssets/, 'Existing work hydrates asset snapshot')
assertMatch(workEditSections.script, /assetSnapshotState\s*=\s*ref<[^>]*>\(\s*'loading'\s*\)/, 'Existing work asset snapshot starts loading')
const loadAssetSnapshotBody = extractFunctionBlock(
  workEditSections.script,
  /async\s+function\s+loadAssetSnapshot\s*\([^)]*\)/,
  'loadAssetSnapshot',
)
assertMatch(loadAssetSnapshotBody, /assetSnapshotState\.value\s*=\s*'ready'/, 'Work asset snapshot ready state')
assertMatch(loadAssetSnapshotBody, /assetSnapshotState\.value\s*=\s*'error'/, 'Work asset snapshot error state')
assertMatch(workEditSections.script, /let\s+assetSnapshotRequestRevision\s*=\s*0/, 'Work asset snapshot requests have an independent revision')
assertMatch(loadAssetSnapshotBody, /const\s+requestRevision\s*=\s*\+\+assetSnapshotRequestRevision[\s\S]*await\s+getActorWorkAssets/, 'Work asset snapshot increments its request revision before loading')
assertEqual(
  [...loadAssetSnapshotBody.matchAll(/requestRevision\s*!==\s*assetSnapshotRequestRevision/g)].length,
  2,
  'Only the latest work asset snapshot request can commit success or failure state',
)
assertMatch(
  loadAssetSnapshotBody,
  /await\s+getActorWorkAssets[\s\S]*if\s*\(\s*requestRevision\s*!==\s*assetSnapshotRequestRevision\s*\)\s*return[\s\S]*assetSnapshotState\.value\s*=\s*'ready'[\s\S]*catch[\s\S]*if\s*\(\s*requestRevision\s*!==\s*assetSnapshotRequestRevision\s*\)\s*return[\s\S]*assetSnapshotState\.value\s*=\s*'error'/,
  'Stale work asset snapshot requests return before writing ready or error state',
)
const retryAssetSnapshotBody = extractFunctionBlock(
  workEditSections.script,
  /async\s+function\s+retryAssetSnapshot\s*\([^)]*\)/,
  'retryAssetSnapshot',
)
assertMatch(retryAssetSnapshotBody, /assetSnapshotState\.value\s*===\s*'loading'[\s\S]*return/, 'Work asset snapshot retry is disabled while a request is loading')
assertMatch(retryAssetSnapshotBody, /loadAssetSnapshot\(workId\.value\)/, 'Work asset snapshot exposes a retry')
assertMatch(
  workEditSections.script,
  /assetRelationsBlocked\s*=\s*computed\(\(\)\s*=>\s*assetSnapshotState\.value\s*===\s*'ready'\s*&&\s*assetSnapshot\.value\.some\(\s*\(asset\)\s*=>\s*asset\.processStatus\s*!==\s*'ready'\s*\)\)/,
  'Any non-ready existing work relation blocks the complete relation editor',
)
assertMatch(workEditSections.script, /assetEditingLocked\s*=\s*computed\([\s\S]{0,220}assetRelationsBlocked\.value/, 'Non-ready existing relations lock every asset edit')
assertNoMatch(workEditSections.script, /textEditingLocked\s*=\s*computed\([\s\S]{0,220}assetRelationsBlocked\.value/, 'Non-ready existing relations do not lock work text editing')
assertNoMatch(saveWorkBody, /assetRelationsBlocked\.value/, 'Text-only save remains available while existing relations are non-ready')
assertMatch(
  workEditSections.template,
  /v-if="assetRelationsBlocked"[\s\S]{0,500}retryAssetSnapshot[\s\S]{0,300}刷新素材状态/,
  'Blocked work relations expose an explicit snapshot refresh action',
)
const openAssetSelectorBody = extractFunctionBlock(
  workEditSections.script,
  /function\s+openAssetSelector\s*\(\s*\)\s*:\s*void/,
  'openAssetSelector',
)
assertMatch(openAssetSelectorBody, /if\s*\(\s*assetEditingLocked\.value\s*\)\s*return/, 'Unknown or non-ready snapshots cannot open the work asset selector')
assertMatch(openAssetSelectorBody, /setWorkSelection\([\s\S]*navigateTo\(\{\s*url:\s*'\/pkg-profile\/assets\/index\?mode=work-select'/, 'Selector receives complete current collection')
function assertWorkEditorOnShowContract(source, label) {
  const body = extractFunctionBlock(source, /onShow\(\s*\(\)\s*=>/, label)
  assertMatch(body, /selectionStore\.consumeWorkSelection\(\)/, `${label} consumes the one-shot selection`)
  assertMatch(body, /selection\s*===\s*null[\s\S]{0,180}assetSnapshotState\.value\s*!==\s*'ready'[\s\S]{0,180}bindingPending\.value[\s\S]{0,80}return/, `${label} rejects unavailable or locked selections`)
  assertMatch(body, /selectedAssets\.value\s*=\s*normalizeAssets\(selection\)/, `${label} normalizes the complete selection`)
  assertMatch(body, /assetsDirty\.value\s*=\s*!bindingsEqual\(selectedAssets\.value,\s*assetSnapshot\.value\)/, `${label} recomputes relation dirtiness`)
  assertNoMatch(body, /bindingError\.value\s*=\s*''/, `${label} preserves an ambiguous binding retry`)
}
assertWorkEditorOnShowContract(workEditSections.script, 'work editor onShow')
assertMutationTurnsGateRed(
  workEditSections.script,
  'const selection = selectionStore.consumeWorkSelection();',
  'const selection = null;',
  assertWorkEditorOnShowContract,
  'work editor onShow selection consumption removal',
)
const normalizeAssetsBody = extractFunctionBlock(
  workEditSections.script,
  /function\s+normalizeAssets\s*\(\s*assets:\s*ActorWorkAsset\[\]\s*\)\s*:\s*ActorWorkAsset\[\]/,
  'normalizeAssets',
)
assertNoMatch(normalizeAssetsBody, /processStatus[\s\S]{0,40}ready|ready[\s\S]{0,40}processStatus/, 'Work snapshot normalization preserves non-ready existing relations')
assertMatch(normalizeAssetsBody, /asset\.mediaType\s*===\s*'photo'\s*\|\|\s*asset\.mediaType\s*===\s*'video'/, 'Work snapshot normalization only excludes unsupported media types')
assertMatch(normalizeAssetsBody, /mediaType\s*===\s*'photo'\s*\?\s*'still'\s*:\s*'clip'/, 'Photo and video usage normalization')
assertMatch(normalizeAssetsBody, /sortNo:\s*index\s*\+\s*1/, 'Each usage receives continuous numeric sort')
assertMatch(workEditSections.script, /assetsDirty/, 'Work asset edits track dirty state')
assertMatch(saveWorkBody, /const\s+savedWork\s*=\s*workId\.value\s*\?[\s\S]*updateActorWork[\s\S]*:\s*await\s+createActorWork/, 'Create returns the saved work ID source')
assertMatch(saveWorkBody, /savedWorkId\.value\s*=\s*savedWork\.experienceId/, 'Saved work ID is retained for binding retry')
assertMatch(workEditSections.script, /textBaseline\s*=\s*ref\(\s*''\s*\)/, 'Work text payload has a saved baseline')
assertMatch(workEditSections.script, /textSaveFailed\s*=\s*ref\(\s*false\s*\)/, 'Failed text save remains dirty')
assertMatch(workEditSections.script, /textDirty\s*=\s*computed\([\s\S]{0,220}buildWorkSavePayload\(\)[\s\S]{0,220}textBaseline\.value/, 'Text dirty compares the complete save payload baseline')
assertMatch(workEditSections.script, /isDirty\s*=\s*computed\(\(\)\s*=>[\s\S]{0,160}textSaveFailed\.value[\s\S]{0,160}textDirty\.value[\s\S]{0,160}assetsDirty\.value/, 'Unified work dirty state includes failed text save, text, and assets')
assertMatch(hydrateWorkBody, /textBaseline\.value\s*=\s*serializeWorkPayload\(buildWorkSavePayload\(\)\)/, 'Hydrated detail establishes the text baseline')
assertMatch(saveWorkBody, /savedWorkId\.value\s*=\s*savedWork\.experienceId[\s\S]{0,260}textBaseline\.value\s*=\s*serializeWorkPayload\(payload\)[\s\S]{0,260}if\s*\(assetsDirty\.value\)/, 'Successful text save updates baseline before relation replacement')
assertMatch(saveWorkBody, /catch\s*\(error\)\s*\{[\s\S]{0,180}textSaveFailed\.value\s*=\s*true/, 'Failed create or update stays dirty')
assertMatch(saveWorkBody, /if\s*\(assetsDirty\.value\)[\s\S]*replaceActorWorkAssets/, 'Bindings replace once only when dirty')
assertEqual(
  [...saveWorkBody.matchAll(/replaceActorWorkAssets\s*\(/g)].length,
  1,
  'Primary work save replaces the complete relation collection exactly once',
)
assertMatch(saveWorkBody, /replaceActorWorkAssets\(savedWork\.experienceId,\s*toBindings\(selectedAssets\.value\)\)/, 'Dirty save submits the complete target collection through toBindings')
assertMatch(
  saveWorkBody,
  /catch\s*\(error\)\s*\{[\s\S]{0,220}bindingError\.value\s*=[\s\S]{0,160}\breturn\s*;?[\s\S]{0,180}finally\s*\{[\s\S]{0,120}bindingPending\.value\s*=\s*false[\s\S]{0,180}finishSave\(\)/,
  'Relation failure returns before the success navigation path',
)
assertMatch(workEditSections.script, /async\s+function\s+retryAssetBinding\s*\([^)]*\)[\s\S]*replaceActorWorkAssets/, 'Binding retry only replaces relations')
const retryAssetBindingBody = extractFunctionBlock(
  workEditSections.script,
  /async\s+function\s+retryAssetBinding\s*\([^)]*\)/,
  'retryAssetBinding',
)
assertNoMatch(retryAssetBindingBody, /if\s*\(\s*!assetsDirty\.value\s*\)/, 'Binding retry always replays the complete target after an ambiguous failure')
assertNoMatch(retryAssetBindingBody, /bindingsEqual|if\s*\([^)]*assetSnapshot\.value[^)]*\)/, 'Binding retry never trusts the pre-failure snapshot after an ambiguous result')
assertEqual(
  [...retryAssetBindingBody.matchAll(/replaceActorWorkAssets\s*\(/g)].length,
  1,
  'Binding retry replays the complete target exactly once',
)
assertNoMatch(retryAssetBindingBody, /createActorWork|updateActorWork|sourceType/, 'Binding retry never resaves work or invents provenance')
const removeAssetBody = extractFunctionBlock(
  workEditSections.script,
  /function\s+removeAsset\s*\(\s*assetId:\s*number\s*\)\s*:\s*void/,
  'removeAsset',
)
assertNoMatch(removeAssetBody, /bindingError\.value\s*=\s*''/, 'Removing an asset keeps the replace-only retry path')
assertMatch(workEditSections.template, /关联素材/, 'Work asset section is visible')
assertMatch(workEditSections.template, /重新加载/, 'Snapshot error exposes reload')
assertMatch(workEditSections.template, /retryAssetBinding/, 'Binding error exposes retry')
assertMatch(workEditSections.template, /bindingPending/, 'Pending binding locks asset editing')
assertMatch(workEditSections.template, /statusLabel\(asset\.processStatus\)/, 'Existing work relations display their process status')
assertMatch(workEditSections.template, /:disabled="assetEditingLocked\s*\|\|\s*asset\.processStatus\s*!==\s*'ready'"/, 'Non-ready existing work relations cannot be removed')
assertMatch(workEditSections.template, /textEditingLocked/, 'Binding second phase locks text editing')
assertEqual(
  [...workEditSections.template.matchAll(/:disabled="textEditingLocked"/g)].length,
  12,
  'All work text fields and pickers are locked during the binding second phase',
)
assertMatch(workEditSections.script, /function\s+polishDescription[\s\S]{0,180}textEditingLocked\.value/, 'Description polish is locked during the binding second phase')
assertMatch(workEditSections.script, /leavingAfterSave/, 'Delayed successful navigation keeps the editor locked')
const workEditGoBackBody = extractFunctionBlock(
  workEditSections.script,
  /function\s+goBack\s*\(\s*\)\s*:\s*void/,
  'work editor goBack',
)
const requestWorkLeaveBody = extractFunctionBlock(
  workEditSections.script,
  /function\s+requestLeave\s*\(\s*\)\s*:\s*void/,
  'work editor requestLeave',
)
const showDiscardWorkBody = extractFunctionBlock(
  workEditSections.script,
  /function\s+showDiscardConfirmation\s*\(\s*\)\s*:\s*void/,
  'showDiscardConfirmation',
)
const onBackPressBody = extractFunctionBlock(
  workEditSections.script,
  /onBackPress\s*\(\s*\(\s*\)\s*=>/,
  'work editor onBackPress',
)
assertMatch(workEditGoBackBody, /bindingPending\.value/, 'Pending binding locks page return')
assertMatch(workEditGoBackBody, /bindingError\.value/, 'Failed binding locks page return')
assertMatch(workEditGoBackBody, /leavingAfterSave\.value/, 'Delayed successful navigation locks page return')
assertMatch(workEditGoBackBody, /requestLeave\(\)/, 'Ordinary floating back uses dirty-leave handling')
assertMatch(requestWorkLeaveBody, /if\s*\(\s*!isDirty\.value\s*\)[\s\S]{0,100}uni\.navigateBack\(\)[\s\S]{0,100}showDiscardConfirmation\(\)/, 'Clean work leaves directly and dirty work confirms')
assertMatch(showDiscardWorkBody, /if\s*\(leaveConfirmPending\.value\)\s*return[\s\S]{0,100}leaveConfirmPending\.value\s*=\s*true/, 'Dirty-leave confirmation cannot open twice')
assertMatch(showDiscardWorkBody, /uni\.showModal\(\{[\s\S]*confirmText:\s*'放弃修改'[\s\S]*if\s*\(result\.confirm\)[\s\S]*uni\.navigateBack\(\)[\s\S]*complete:[\s\S]*leaveConfirmPending\.value\s*=\s*false/, 'Dirty work uses a native discard confirmation')
assertMatch(onBackPressBody, /saving\.value[\s\S]*bindingPending\.value[\s\S]*leavingAfterSave\.value[\s\S]*bindingError\.value/, 'System back is hard-locked during the binding second phase')
assertMatch(onBackPressBody, /isDirty\.value[\s\S]*showDiscardConfirmation\(\)/, 'System back confirms dirty work')
function assertWorkEditorNeutralShell(source, label) {
  assertNeutralProfilePackageShell(source, extractSfcSections(source, `${label} SFC`), 'work-edit', label, {
    groupSelectors: [/\.work-edit__detail-state\s*/, /\.work-edit__section\s*/],
    primaryActionSelectors: [/\.work-edit__footer\s+button\s*/],
    buttonSelectors: [
      /\.work-edit__detail-state\s+button\s*/,
      /\.work-edit__asset-action,\s*\.work-edit__asset-state\s+button,\s*\.work-edit__binding-error\s+button\s*/,
      /\.work-edit__asset-blocked\s+button\s*/,
      /\.work-edit__footer\s+button\s*/,
    ],
  })
}
assertWorkEditorNeutralShell(workEditPage, 'Work editor')
assertStyleBlock(workEditSections.style, /\.work-edit__footer\s*/, /position:\s*fixed/, 'Work editor keeps a fixed action bar')
assertStyleBlock(workEditSections.style, /\.work-edit__footer\s*/, /env\(safe-area-inset-bottom\)/, 'Work editor action bar reserves safe area')
assertStyleBlock(workEditSections.style, /\.work-edit__footer\s*/, /height:\s*calc\(116rpx\s*\+\s*env\(safe-area-inset-bottom\)\)/, 'Work editor action bar has exact total height')
assertStyleBlock(workEditSections.style, /\.work-edit__footer\s*/, /box-sizing:\s*border-box/, 'Work editor action bar includes padding in its total height')
assertStyleBlock(workEditSections.style, /\.work-edit__footer\s*/, /padding:\s*14rpx\s+\$kp-spacing-page\s+calc\(14rpx\s*\+\s*env\(safe-area-inset-bottom\)\)/, 'Work editor action bar keeps 14rpx button padding')
assertStyleBlock(workEditSections.style, /\.work-edit__footer\s+button\s*/, /height:\s*88rpx/, 'Work editor action button has stable height')
assertStyleBlock(workEditSections.style, /\.work-edit__bottom-space\s*/, /height:\s*calc\(116rpx\s*\+\s*env\(safe-area-inset-bottom\)\)/, 'Work editor content reserves the exact footer height')
assertStyleBlock(workEditSections.style, /\.work-edit__detail-state\s*/, /padding:\s*\d+rpx\s+\$kp-spacing-page/, 'Work detail state has stable page padding')
assertStyleBlock(workEditSections.style, /\.work-edit__detail-state\s*/, /border-bottom:\s*1rpx\s+solid\s+\$kp-color-divider/, 'Work detail state uses the shared divider')
assertStyleBlock(workEditSections.style, /\.work-edit__detail-state--error\s*/, /color:\s*\$kp-color-danger/, 'Work detail error is visibly distinguished')
assertStyleBlock(workEditSections.style, /\.work-edit__footer\s*/, /border-top:\s*0/, 'Footer divider does not consume the fixed height')
assertStyleBlock(workEditSections.style, /\.work-edit__footer::before\s*/, /height:\s*1rpx/, 'Footer renders a non-layout silver divider')
assertNoMatch(workEditSections.style, /box-sizing:\s*content-box/, 'Work editor has no content-box fixed footer')

const assetsPage = await readText('kaipai-frontend/src/pkg-profile/assets/index.vue')
const assetsPageSections = extractSfcSections(assetsPage, 'Asset library SFC')
assertMatch(
  assetsPageSections.script,
  /portrait_candidate[\s\S]*model_card[\s\S]*portrait[\s\S]*lifestyle[\s\S]*production[\s\S]*costume[\s\S]*self_intro[\s\S]*work_clip[\s\S]*performance_clip[\s\S]*resume/,
  'Asset library defines every formal photo video and PDF category code',
)
assertMatch(assetsPageSections.script, /avatar:\s*'头像候选'[\s\S]*work_still:\s*'剧照'/, 'Asset library displays legacy category codes compatibly')
assertMatch(assetsPageSections.template, /categoryLabel\(asset\)/, 'Asset rows display localized category labels')
assertNoMatch(assetsPageSections.template, /asset\.categoryCode\s*\|\|/, 'Asset rows never expose raw category codes')
function assertCanonicalAssetCategoryContract(source, label) {
  const body = extractFunctionBlock(
    source,
    /function\s+canonicalCategoryCode\s*\(\s*asset:\s*ActorAsset\s*\)\s*:\s*string\s*\|\s*undefined/,
    label,
  )
  assertMatch(body, /asset\.categoryCode\s*===\s*'avatar'[\s\S]{0,120}portrait_candidate/, `${label} canonicalizes legacy avatar writes`)
  assertMatch(body, /asset\.categoryCode\s*===\s*'work_still'[\s\S]{0,120}production/, `${label} canonicalizes legacy work-still writes`)
  assertNoMatch(body, /return\s+['"](?:avatar|work_still)['"]/, `${label} never emits legacy category codes`)
}
assertCanonicalAssetCategoryContract(assetsPageSections.script, 'canonicalCategoryCode')
assertMutationTurnsGateRed(
  assetsPageSections.script,
  "if (asset.categoryCode === 'avatar') return 'portrait_candidate';",
  "if (asset.categoryCode === 'avatar') return 'avatar';",
  assertCanonicalAssetCategoryContract,
  'legacy avatar category canonicalization removal',
)
assertMatch(assetsPageSections.template, /failureMessage/, 'Failed asset rows display their server failure reason')
const openAssetActionsBody = extractFunctionBlock(
  assetsPageSections.script,
  /function\s+openActions\s*\(\s*asset:\s*ActorAsset\s*\)\s*:\s*void/,
  'openActions',
)
assertMatch(openAssetActionsBody, /修改分类/, 'Asset action menu supports category changes')
function assertOpenAssetActionsResumeEligibilityContract(source, label) {
  const body = extractFunctionBlock(
    source,
    /function\s+openActions\s*\(\s*asset:\s*ActorAsset\s*\)\s*:\s*void/,
    label,
  )
  assertMatch(
    body,
    /const\s+items\s*=\s*\[\s*'预览'\s*,\s*'重命名'\s*,\s*'修改分类'[\s\S]{0,180}'删除'\s*\]\s*;/,
    `${label} keeps preview rename category and delete actions for every asset state`,
  )
  assertMatch(
    body,
    /\.\.\.\(\s*asset\.mediaType\s*===\s*'pdf'\s*&&\s*asset\.processStatus\s*===\s*'ready'\s*\?\s*\[\s*'设为当前 PDF'\s*\]\s*:\s*\[\s*\]\s*\)/,
    `${label} exposes the current-PDF action only for ready PDFs`,
  )
}
assertOpenAssetActionsResumeEligibilityContract(assetsPageSections.script, 'openActions resume eligibility')
assertMutationTurnsGateRed(
  assetsPageSections.script,
  "asset.mediaType === 'pdf' && asset.processStatus === 'ready'",
  "asset.mediaType === 'pdf'",
  assertOpenAssetActionsResumeEligibilityContract,
  'asset current-PDF action readiness guard removal',
  {
    requireUnique: true,
    expectedFailurePattern: /exposes the current-PDF action only for ready PDFs/,
  },
)
function assertSetResumeEligibilityContract(source, label) {
  const body = extractFunctionBlock(
    source,
    /async\s+function\s+setResume\s*\(\s*asset:\s*ActorAsset\s*\)\s*:\s*Promise<void>/,
    label,
  )
  assertMatch(
    body,
    /^\s*if\s*\(\s*asset\.mediaType\s*!==\s*'pdf'\s*\|\|\s*asset\.processStatus\s*!==\s*'ready'\s*\)\s*return\s*;/,
    `${label} fails closed before setting a non-ready or non-PDF resume`,
  )
  assertMatch(body, /setCurrentResume\(asset\.assetId\)/, `${label} keeps the current-resume API call for eligible assets`)
}
assertSetResumeEligibilityContract(assetsPageSections.script, 'setResume eligibility')
assertMutationTurnsGateRed(
  assetsPageSections.script,
  "if (asset.mediaType !== 'pdf' || asset.processStatus !== 'ready') return;",
  "if (asset.mediaType !== 'pdf') return;",
  assertSetResumeEligibilityContract,
  'setResume ready fail-closed guard removal',
  {
    requireUnique: true,
    expectedFailurePattern: /fails closed before setting a non-ready or non-PDF resume/,
  },
)
function assertRenameAssetCategoryContract(source, label) {
  const body = extractFunctionBlock(
    source,
    /async\s+function\s+rename\s*\(\s*asset:\s*ActorAsset\s*\)\s*:\s*Promise<void>/,
    label,
  )
  assertMatch(body, /updateActorAsset\(asset\.assetId,\s*\{\s*originalName:[\s\S]{0,160}categoryCode:\s*canonicalCategoryCode\(asset\)/, `${label} preserves a canonical current category`)
}
assertRenameAssetCategoryContract(assetsPageSections.script, 'rename asset')
assertMutationTurnsGateRed(
  assetsPageSections.script,
  'categoryCode: canonicalCategoryCode(asset)',
  'categoryCode: asset.categoryCode || undefined',
  assertRenameAssetCategoryContract,
  'asset rename category canonicalization removal',
)
const changeAssetCategoryBody = extractFunctionBlock(
  assetsPageSections.script,
  /async\s+function\s+changeCategory\s*\(\s*asset:\s*ActorAsset\s*\)\s*:\s*Promise<void>/,
  'changeCategory',
)
assertMatch(changeAssetCategoryBody, /categoryOptions\(asset\.mediaType\)/, 'Category menu is limited to the current media type')
assertMatch(changeAssetCategoryBody, /updateActorAsset\(asset\.assetId,\s*\{\s*originalName:\s*asset\.originalName,[\s\S]{0,160}categoryCode:/, 'Category change preserves the current original name')
assertMatch(assetsPageSections.template, /loadError[\s\S]{0,500}retryPageLoad[\s\S]{0,200}重新加载/, 'Asset page errors remain inline and retryable')
assertMatch(assetsPageSections.script, /assetPageStates\s*=\s*reactive/, 'Asset pages retain successful data independently per media type')
const loadAssetPageBody = extractFunctionBlock(
  assetsPageSections.script,
  /async\s+function\s+load\s*\(\s*reset:\s*boolean\s*\)\s*:\s*Promise<void>/,
  'asset page load',
)
assertMatch(loadAssetPageBody, /catch\s*\(error\)[\s\S]{0,300}\.error\s*=/, 'Asset page converts list failures to inline state')
assertMatch(loadAssetPageBody, /catch\s*\(error\)[\s\S]{0,360}retryReset\s*=\s*reset/, 'Asset page records whether the failed request was reset or next-page')
assertNoMatch(loadAssetPageBody, /catch\s*\(error\)[\s\S]{0,300}(?:assets|list)\.value\s*=\s*\[\]/, 'Asset list failures never erase a successful page')
assertMatch(loadAssetPageBody, /const\s+requestRevision\s*=\s*\+\+assetRequestRevision/, 'Asset load advances the list request revision')
assertMatch(loadAssetPageBody, /const\s+requestedMediaType\s*=\s*mediaType\.value/, 'Asset load snapshots its requested tab')
assertMatch(loadAssetPageBody, /requestRevision\s*!==\s*assetRequestRevision\s*\|\|\s*requestedMediaType\s*!==\s*mediaType\.value/, 'Stale asset tab responses cannot update the visible list')
assertMutationTurnsGateRed(
  assetsPageSections.script,
  'pageState.retryReset = reset;',
  'pageState.retryReset = null;',
  (source, label) => {
    const body = extractFunctionBlock(source, /async\s+function\s+load\s*\(\s*reset:\s*boolean\s*\)\s*:\s*Promise<void>/, label)
    assertMatch(body, /retryReset\s*=\s*reset/, `${label} records the exact failed request mode`)
  },
  'asset load retry-mode recording removal',
)
const retryAssetPageLoadBody = extractFunctionBlock(
  assetsPageSections.script,
  /function\s+retryPageLoad\s*\(\s*\)\s*:\s*void/,
  'retryPageLoad',
)
assertMatch(retryAssetPageLoadBody, /retryReset[\s\S]{0,180}load\(retryReset\)/, 'Asset page retry exactly replays the failed reset or next-page action')
const switchAssetTypeBody = extractFunctionBlock(
  assetsPageSections.script,
  /function\s+switchType\s*\(\s*type:\s*ActorAssetMediaType\s*\)\s*:\s*void/,
  'switchType',
)
assertNoMatch(switchAssetTypeBody, /assets\.value\s*=\s*\[\]/, 'Switching tabs preserves that tab previous successful page')
function assertScheduleAssetPollingContract(source, label) {
  const body = extractFunctionBlock(
    source,
    /function\s+scheduleAssetPolling\s*\(\s*\)\s*:\s*void/,
    label,
  )
  assertMatch(body, /^\s*const\s+requestRevision\s*=\s*\+\+assetPollRevision;/, `${label} invalidates stale requests before inspecting IDs`)
  assertMatch(body, /if\s*\(\s*!assetIds\.length\s*\)\s*\{[\s\S]{0,100}return;/, `${label} keeps the new revision when no IDs remain`)
  assertMatch(body, /asset\.processStatus\s*===\s*'uploading'[\s\S]{0,120}asset\.processStatus\s*===\s*'processing'/, `${label} schedules only formal non-terminal states`)
  assertMatch(body, /assetPollAttempts\.get\(asset\.assetId\)[\s\S]{0,120}<\s*MAX_ASSET_POLL_ATTEMPTS/, `${label} enforces the bounded attempt count`)
  assertMatch(body, /setTimeout\([\s\S]{0,220}pollAssetStatuses\(assetIds,\s*requestRevision\)/, `${label} polls only the captured bounded IDs`)
}
assertScheduleAssetPollingContract(assetsPageSections.script, 'scheduleAssetPolling')
assertMutationTurnsGateRed(
  assetsPageSections.script,
  'const requestRevision = ++assetPollRevision;\n  if (assetPollTimer !== null) clearTimeout(assetPollTimer);',
  'if (assetPollTimer !== null) clearTimeout(assetPollTimer);',
  (source, label) => {
    const body = extractFunctionBlock(source, /function\s+scheduleAssetPolling\s*\(\s*\)\s*:\s*void/, label)
    const invalidatesNoId = /^\s*const\s+requestRevision\s*=\s*\+\+assetPollRevision;/.test(body)
    let revision = 7
    let assetStatus = 'ready'
    if (invalidatesNoId) revision += 1
    const stalePollRevision = 7
    if (stalePollRevision === revision) assetStatus = 'processing'
    assertEqual(assetStatus, 'ready', `${label} must not allow a stale poll to regress a ready asset`)
  },
  'asset polling no-id revision invalidation removal',
)
assertMutationTurnsGateRed(
  assetsPageSections.script,
  "(asset.processStatus === 'uploading' || asset.processStatus === 'processing')",
  "asset.processStatus === 'processing'",
  assertScheduleAssetPollingContract,
  'asset polling uploading-state removal',
)
assertMutationTurnsGateRed(
  assetsPageSections.script,
  /\(assetPollAttempts\.get\(asset\.assetId\)\s*\|\|\s*0\)\s*<\s*MAX_ASSET_POLL_ATTEMPTS/,
  '(assetPollAttempts.get(asset.assetId) || 0) < Number.MAX_SAFE_INTEGER',
  assertScheduleAssetPollingContract,
  'asset polling attempt-bound removal',
)
const pollAssetStatusesBody = extractFunctionBlock(
  assetsPageSections.script,
  /async\s+function\s+pollAssetStatuses\s*\([^)]*\)\s*:\s*Promise<void>/,
  'pollAssetStatuses',
)
assertMatch(pollAssetStatusesBody, /getActorAsset\([\s\S]{0,220}showLoading:\s*false[\s\S]{0,120}showError:\s*false/, 'Asset polling is silent')
assertNoMatch(pollAssetStatusesBody, /load\(\s*true\s*\)/, 'Asset polling merges rows without replacing the paged list')
const stopAssetPollingBody = extractFunctionBlock(
  assetsPageSections.script,
  /function\s+stopAssetPolling\s*\(\s*\)\s*:\s*void/,
  'stopAssetPolling',
)
assertMatch(stopAssetPollingBody, /clearTimeout[\s\S]{0,160}assetPollRevision\s*\+=\s*1/, 'Stopping asset polling clears the timer and invalidates stale requests')
function assertAssetLifecycleStopContract(source, signaturePattern, label) {
  const body = extractFunctionBlock(source, signaturePattern, label)
  assertMatch(body, /pageActive\s*=\s*false/, `${label} marks the page inactive`)
  assertMatch(body, /stopAssetPolling\(\)/, `${label} invalidates in-flight polling`)
}
assertAssetLifecycleStopContract(assetsPageSections.script, /onHide\(\s*\(\)\s*=>/, 'asset library onHide')
assertAssetLifecycleStopContract(assetsPageSections.script, /onUnload\(\s*\(\)\s*=>/, 'asset library onUnload')
assertMutationTurnsGateRed(
  assetsPageSections.script,
  /onHide\(\(\)\s*=>\s*\{\n\s*pageActive\s*=\s*false;\n\s*stopAssetPolling\(\);/,
  'onHide(() => {\n  pageActive = false;',
  (source, label) => assertAssetLifecycleStopContract(source, /onHide\(\s*\(\)\s*=>/, label),
  'asset library onHide polling-stop removal',
)
assertMutationTurnsGateRed(
  assetsPageSections.script,
  /onUnload\(\(\)\s*=>\s*\{\n\s*pageActive\s*=\s*false;\n\s*stopAssetPolling\(\);/,
  'onUnload(() => {\n  pageActive = false;',
  (source, label) => assertAssetLifecycleStopContract(source, /onUnload\(\s*\(\)\s*=>/, label),
  'asset library onUnload polling-stop removal',
)
assertMatch(assetsPageSections.template, /uploadError[\s\S]{0,500}retryUpload[\s\S]{0,200}重试上传/, 'Failed uploads expose an in-page retry')
assertMatch(assetsPageSections.script, /pendingUpload\s*=\s*ref<PendingUpload\s*\|\s*null>/, 'Failed upload retry data stays in page memory')
assertNoMatch(assetsPageSections.script, /setStorage|localStorage|persist/, 'Temporary upload paths are never persisted')
const defaultUploadCategoryBody = extractFunctionBlock(
  assetsPageSections.script,
  /function\s+defaultUploadCategory\s*\(\s*type:\s*ActorAssetMediaType\s*\)\s*:\s*string/,
  'defaultUploadCategory',
)
assertMatch(defaultUploadCategoryBody, /avatar-select[\s\S]{0,180}portrait_candidate[\s\S]{0,180}pdf[\s\S]{0,120}resume[\s\S]{0,120}other/, 'New uploads use formal avatar PDF and default category codes')
const performAssetUploadBody = extractFunctionBlock(
  assetsPageSections.script,
  /async\s+function\s+performUpload\s*\(\s*pending:\s*PendingUpload\s*\)\s*:\s*Promise<void>/,
  'performUpload',
)
assertMatch(performAssetUploadBody, /if\s*\(\s*uploading\.value\s*\)\s*return/, 'Asset upload has a duplicate-submit guard')
assertMatch(performAssetUploadBody, /catch\s*\(error\)[\s\S]{0,260}pendingUpload\.value\s*=[\s\S]{0,180}uploadError\.value\s*=/, 'Failed upload retains its retry payload and inline error')
const retryUploadBody = extractFunctionBlock(
  assetsPageSections.script,
  /function\s+retryUpload\s*\(\s*\)\s*:\s*void/,
  'retryUpload',
)
assertMatch(retryUploadBody, /pendingUpload\.value[\s\S]{0,160}performUpload/, 'Upload retry reuses only the in-memory pending payload')
assertMatch(assetsPageSections.template, /asset\.mediaType\s*===\s*'pdf'\s*&&\s*asset\.processStatus\s*===\s*'failed'[\s\S]{0,300}retryFailedPdf[\s\S]{0,180}重新上传并处理/, 'Only failed PDF rows expose re-upload processing')
const retryFailedPdfBody = extractFunctionBlock(
  assetsPageSections.script,
  /async\s+function\s+retryFailedPdf\s*\(\s*asset:\s*ActorAsset\s*\)\s*:\s*Promise<void>/,
  'retryFailedPdf',
)
assertMatch(retryFailedPdfBody, /choosePdf\(\)[\s\S]{0,260}retryActorPdfAsset\(asset\.assetId,\s*filePath\)/, 'Failed PDF retry selects a fresh PDF and calls the retry API')
assertMatch(retryFailedPdfBody, /catch\s*\(error\)[\s\S]{0,220}pdfRetryError\.value\s*=/, 'Failed PDF retry remains visible and actionable')
assertNoMatch(retryFailedPdfBody, /deleteActorAsset|updateActorAsset/, 'PDF retry never mutates or removes the old failed record')
const handleAssetBody = extractFunctionBlock(
  assetsPageSections.script,
  /async\s+function\s+handleAsset\s*\(\s*asset:\s*ActorAsset\s*\)\s*:\s*Promise<void>/,
  'handleAsset',
)
assertMatch(handleAssetBody, /mode\.value\s*===\s*'avatar-select'[\s\S]*selectionStore\.selectAvatar\(\{\s*assetId:\s*asset\.assetId\s*\}\)[\s\S]*uni\.navigateBack\(\)/, 'Avatar selector returns only the selected ID')
assertNoMatch(handleAssetBody, /mode\.value\s*===\s*'avatar-select'[\s\S]*requestAssetAccessUrl[\s\S]*selectAvatar/, 'Avatar selector does not sign a URL before returning')
const normalizeWorkSelectionBody = extractFunctionBlock(
  assetsPageSections.script,
  /function\s+normalizeWorkSelection\s*\(\s*selection:\s*ActorWorkAsset\[\]\s*\)\s*:\s*ActorWorkAsset\[\]/,
  'normalizeWorkSelection',
)
function assertCompleteWorkSelectionContract(source, label) {
  const body = extractFunctionBlock(
    source,
    /function\s+completeWorkSelection\s*\(\s*\)\s*:\s*void/,
    label,
  )
  assertMatch(body, /selectionStore\.setWorkSelection\(normalizeWorkSelection\(selectedWorkAssets\.value\)\)/, `${label} returns one normalized complete target collection`)
  assertMatch(body, /uni\.navigateBack\(\)/, `${label} returns to the editor after storing the selection`)
}
function assertAssetsOnLoadContract(source, label) {
  const body = extractFunctionBlock(source, /onLoad\(\s*\(query\)\s*=>/, label)
  assertMatch(body, /mode\.value\s*=\s*String\(query\?\.mode\s*\|\|\s*''\)/, `${label} reads the route mode`)
  assertMatch(body, /mode\.value\s*===\s*'avatar-select'[\s\S]{0,100}mediaType\.value\s*=\s*'photo'/, `${label} opens avatar selection on photos`)
  assertMatch(body, /mode\.value\s*===\s*'work-select'[\s\S]{0,180}selectionStore\.consumeWorkSelection\(\)/, `${label} consumes the editor's complete selection`)
  assertMatch(body, /selectedWorkAssets\.value\s*=\s*normalizeWorkSelection/, `${label} normalizes the incoming selection`)
}
function assertAssetsOnShowContract(source, label) {
  const body = extractFunctionBlock(source, /onShow\(\s*\(\)\s*=>/, label)
  assertMatch(body, /pageActive\s*=\s*true/, `${label} activates polling lifecycle`)
  assertMatch(body, /load\(true\)/, `${label} refreshes the active tab`)
}
assertCompleteWorkSelectionContract(assetsPageSections.script, 'completeWorkSelection')
assertAssetsOnLoadContract(assetsPageSections.script, 'asset library onLoad')
assertAssetsOnShowContract(assetsPageSections.script, 'asset library onShow')
assertMutationTurnsGateRed(
  assetsPageSections.script,
  'selectionStore.setWorkSelection(normalizeWorkSelection(selectedWorkAssets.value));',
  'void normalizeWorkSelection(selectedWorkAssets.value);',
  assertCompleteWorkSelectionContract,
  'completeWorkSelection store handoff removal',
)
assertMutationTurnsGateRed(
  assetsPageSections.script,
  'selectedWorkAssets.value = normalizeWorkSelection(selectionStore.consumeWorkSelection() || []);',
  'selectedWorkAssets.value = normalizeWorkSelection([]);',
  assertAssetsOnLoadContract,
  'asset library onLoad selection consumption removal',
)
assertMutationTurnsGateRed(
  assetsPageSections.script,
  'pageActive = true;',
  'pageActive = false;',
  assertAssetsOnShowContract,
  'asset library onShow activation removal',
)
const toggleWorkAssetBody = extractFunctionBlock(
  assetsPageSections.script,
  /function\s+toggleWorkAsset\s*\(\s*asset:\s*ActorAsset\s*\)\s*:\s*void/,
  'toggleWorkAsset',
)
assertNoMatch(normalizeWorkSelectionBody, /processStatus[\s\S]{0,40}ready|ready[\s\S]{0,40}processStatus/, 'Selector normalization preserves non-ready existing relations')
assertMatch(toggleWorkAssetBody, /asset\.processStatus\s*!==\s*'ready'/, 'Only ready new candidates can be selected')
assertMatch(assetsPageSections.script, /types[\s\S]*photo[\s\S]*video[\s\S]*pdf/, 'Normal asset library retains all media tabs')
assertMatch(assetsPageSections.script, /workTypes[\s\S]*photo[\s\S]*video/, 'Work selector has photo and video tabs')
assertNoMatch(assetsPageSections.script, /workTypes[^;\n]*pdf/, 'Work selector excludes PDF tab')
assertMatch(assetsPageSections.script, /selectedWorkAssetIds/, 'Work selector supports multiple selected assets')
assertMatch(assetsPageSections.script, /processStatus\s*!==\s*'ready'/, 'Non-ready work assets cannot be selected')
assertMatch(assetsPageSections.script, /const\s+PAGE_SIZE\s*=\s*10/, 'Asset selector uses bounded pages')
assertMatch(assetsPageSections.script, /onReachBottom\([\s\S]*loadNextPage/, 'Asset selector can reach assets after the first page')
assertMatch(assetsPageSections.template, /完成（\{\{\s*selectedWorkAssetIds\.size\s*\}\}）/, 'Work selector completion count')
assertMatch(assetsPageSections.template, /processStatus/, 'Work selector keeps processing status visible')
assertStyleBlock(assetsPageSections.style, /\.assets-page__complete-bar\s*/, /position:\s*fixed/, 'Asset selector keeps a fixed completion bar')
assertStyleBlock(assetsPageSections.style, /\.assets-page__complete-bar\s*/, /env\(safe-area-inset-bottom\)/, 'Asset selector completion bar reserves safe area')
assertStyleBlock(assetsPageSections.style, /\.assets-page__complete-bar\s*/, /height:\s*calc\(116rpx\s*\+\s*env\(safe-area-inset-bottom\)\)/, 'Asset selector completion bar has exact total height')
assertStyleBlock(assetsPageSections.style, /\.assets-page__complete-bar\s*/, /box-sizing:\s*border-box/, 'Asset selector completion bar includes padding in its total height')
assertStyleBlock(assetsPageSections.style, /\.assets-page__complete-bar\s*/, /padding:\s*14rpx\s+\$kp-spacing-page\s+calc\(14rpx\s*\+\s*env\(safe-area-inset-bottom\)\)/, 'Asset selector completion bar keeps 14rpx button padding')
assertStyleBlock(assetsPageSections.style, /\.assets-page__complete-bar\s+button\s*/, /height:\s*88rpx/, 'Asset selector completion button has stable height')
assertStyleBlock(assetsPageSections.style, /\.assets-page--select\s*/, /padding-bottom:\s*calc\(116rpx\s*\+\s*env\(safe-area-inset-bottom\)\)/, 'Asset selector content reserves the exact completion bar height')
assertStyleBlock(assetsPageSections.style, /\.assets-page__complete-bar\s*/, /border-top:\s*0/, 'Completion divider does not consume the fixed height')
assertStyleBlock(assetsPageSections.style, /\.assets-page__complete-bar::before\s*/, /height:\s*1rpx/, 'Completion bar renders a non-layout silver divider')
assertNoMatch(assetsPageSections.style, /box-sizing:\s*content-box/, 'Asset selector has no content-box fixed completion bar')
function assertAssetLibraryNeutralShell(source, label) {
  assertNeutralProfilePackageShell(source, extractSfcSections(source, `${label} SFC`), 'assets-page', label, {
    groupSelectors: [/\.assets-page__toolbar\s*/, /\.assets-page__list\s*/],
    primaryActionSelectors: [/\.assets-page__add\s*/, /\.assets-page__complete-bar\s+button\s*/],
    buttonSelectors: [
      /\.assets-page__add\s*/,
      /\.assets-page__pdf-retry\s*/,
      /\.assets-page__error\s+button\s*/,
      /\.assets-page__complete-bar\s+button\s*/,
    ],
  })
}
assertAssetLibraryNeutralShell(assetsPage, 'Asset library')

assertMutationTurnsGateRed(
  importPage,
  /(\.import-review__nav\s*\{[^{}]*\bposition:\s*)sticky(\s*;)/,
  '$1relative$2',
  assertImportReviewNeutralShell,
  'profile import sticky-navigation regression',
)
assertMutationTurnsGateRed(
  worksPage,
  /(\.works-page__nav\s*\{[^{}]*\btop:\s*)0(\s*;)/,
  '$1auto$2',
  assertWorkLibraryNeutralShell,
  'work library navigation top regression',
)
assertMutationTurnsGateRed(
  workEditPage,
  /(\.work-edit__nav\s*\{[^{}]*\bz-index:\s*)30(\s*;)/,
  '$1auto$2',
  assertWorkEditorNeutralShell,
  'work editor navigation layer regression',
)
assertMutationTurnsGateRed(
  importPage,
  /(\.import-review__nav\s*\{[^{}]*)(\})/,
  '$1 position: relative; top: auto; z-index: auto; $2',
  assertImportReviewNeutralShell,
  'profile import same-block navigation override',
)
assertMutationTurnsGateRed(
  worksPage,
  /<\/style>/,
  '.works-page .works-page__nav { position: relative !important; top: auto !important; z-index: 99 !important; }\n</style>',
  assertWorkLibraryNeutralShell,
  'work library higher-specificity navigation override',
)
assertMutationTurnsGateRed(
  importPage,
  /(\.import-review__footer\s*\{[^{}]*\bposition:\s*)fixed(\s*;)/,
  '$1relative$2',
  assertImportReviewNeutralShell,
  'profile import fixed-footer regression',
)
assertMutationTurnsGateRed(
  importPage,
  /(\.import-review__bottom-space\s*\{[^{}]*\bheight:\s*)calc\(118rpx\s*\+\s*env\(safe-area-inset-bottom\)\)(\s*;)/,
  '$1auto$2',
  assertImportReviewNeutralShell,
  'profile import footer-clearance removal',
)
assertMutationTurnsGateRed(
  worksPage,
  /(\.works-page__footer\s*\{[^{}]*\bposition:\s*)fixed(\s*;)/,
  '$1relative$2',
  assertWorkLibraryNeutralShell,
  'work library fixed-footer regression',
)
assertMutationTurnsGateRed(
  worksPage,
  /(\.works-page__footer\s*\{[^{}]*\bpadding:\s*)[^;{}]*env\(safe-area-inset-bottom\)[^;{}]*(\s*;)/,
  '$1unset$2',
  assertWorkLibraryNeutralShell,
  'work library footer safe-area removal',
)
assertMutationTurnsGateRed(
  importPage,
  /(\.import-review__footer\s*\{[^{}]*\bpadding:\s*)14rpx\s+\$kp-spacing-page\s+calc\(14rpx\s*\+\s*env\(safe-area-inset-bottom\)\)(\s*;)/,
  '$1calc(14rpx + env(safe-area-inset-bottom)) $kp-spacing-page 14rpx$2',
  assertImportReviewNeutralShell,
  'profile import footer safe-area top-edge regression',
)
assertMutationTurnsGateRed(
  worksPage,
  /(\.works-page__footer\s*\{[^{}]*\bpadding:\s*)14rpx\s+\$kp-spacing-page\s+calc\(14rpx\s*\+\s*env\(safe-area-inset-bottom\)\)(\s*;)/,
  '$1calc(14rpx + env(safe-area-inset-bottom)) $kp-spacing-page 14rpx$2',
  assertWorkLibraryNeutralShell,
  'work library footer safe-area top-edge regression',
)

assertMutationTurnsGateRed(
  importPage,
  /<KpFloatingBackButton\b[^>]*\/>/,
  '',
  assertImportReviewNeutralShell,
  'profile import rendered back-button removal',
)
assertMutationTurnsGateRed(
  importPage,
  /border-radius:\s*(?:12|14|16)rpx/,
  'border-radius: 50%',
  assertImportReviewNeutralShell,
  'profile import command-button radius regression',
)
assertMutationTurnsGateRed(
  worksPage,
  /\.works-page\s*\{/,
  '.works-page--dead {',
  assertWorkLibraryNeutralShell,
  'work library root selector rename',
)
assertMutationTurnsGateRed(
  worksPage,
  /\.works-page__list\s*\{[^}]*\}/,
  '$&\n.works-page__list { border-radius: 40rpx; }',
  assertWorkLibraryNeutralShell,
  'work library post-declaration group radius override',
)
assertMutationTurnsGateRed(
  worksPage,
  /<\/style>/,
  '.works-page { background: #000; color: #fff; }\n</style>',
  assertWorkLibraryNeutralShell,
  'work library post-declaration root palette override',
)
assertMutationTurnsGateRed(
  worksPage,
  /<\/style>/,
  '.works-page__legacy-theme { color: #191919; }\n</style>',
  assertWorkLibraryNeutralShell,
  'work library legacy cool-gray palette injection',
)
assertMutationTurnsGateRed(
  worksPage,
  /:class="\{\s*'works-page--representative':\s*representativeMode\s*\}"/,
  '',
  assertWorkLibraryNeutralShell,
  'representative footer clearance removal',
)

const favoriteComposable = await readText('kaipai-frontend/src/composables/use-share-card-favorite.ts')
assertMatch(favoriteComposable, /getShareCardFavoriteStatus/, 'Favorite status API')
assertMatch(favoriteComposable, /addShareCardFavorite/, 'Favorite add API')
assertMatch(favoriteComposable, /removeShareCardFavorite/, 'Favorite remove API')
assertMatch(favoriteComposable, /requireLoginForFavorite[\s\S]*goLogin\(\)/, 'Favorite login gate')
for (const path of [
  'kaipai-frontend/src/pages/actor-profile/detail.vue',
  'kaipai-frontend/src/pkg-card/actor-card/index.vue',
  'kaipai-frontend/src/pkg-card/ai-profile-card-detail/index.vue',
]) {
  const publicPage = await readText(path)
  assertMatch(publicPage, /useShareCardFavorite/, `${path} favorite state`)
  assertMatch(publicPage, /toggleFavorite/, `${path} favorite action`)
}

const sourceMutationCount = functionScopedMutationCount
console.log(`Clipboard review-state destructive mutation self-test passed (${destructiveClipboardReviewStateMutations.length}/${destructiveClipboardReviewStateMutations.length}).`)
console.log(`Source function-scoped and shell mutation self-test passed (${sourceMutationCount}/${sourceMutationCount}).`)
console.log('Source gate passed.')
if (sourceOnly) {
  console.log('built artifact verification skipped (--source-only).')
  console.log('Package audit skipped (--source-only).')
} else {
  const { synchronizedArtifactCount, artifactMutationCount } = await verifyBuiltArtifacts()
  console.log(`Built mini-program artifact gate passed (${synchronizedArtifactCount}/${synchronizedArtifactCount} build/dev page files synchronized).`)
  console.log(`Built artifact destructive mutation self-test passed (${artifactMutationCount}/${artifactMutationCount}).`)
  console.log('Running authoritative mini-program package audit...')
  runAuthoritativePackageAudit()
  console.log('Authoritative mini-program package audit passed.')
}
console.log('Mini-program career profile hub static gate passed.')
