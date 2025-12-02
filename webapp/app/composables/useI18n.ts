import { translations, type Language, type TranslationKey } from '~/utils/i18n'

export const useI18n = () => {
  const language = useCookie<Language>('language', {
    default: () => 'en',
    watch: true
  })

  const t = (key: TranslationKey): string => {
    return translations[language.value][key] || key
  }

  const setLanguage = (lang: Language) => {
    language.value = lang
  }

  return {
    t,
    language: readonly(language),
    setLanguage
  }
}
