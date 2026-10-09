import eslintPluginAstro from 'eslint-plugin-astro';
import eslintConfigPrettier from 'eslint-config-prettier';
import tsParser from '@typescript-eslint/parser';

export default [
  ...eslintPluginAstro.configs['flat/recommended'],
  eslintConfigPrettier,
  {
    files: ['**/*.astro'],
    languageOptions: {
      parserOptions: {
        parser: tsParser,
      },
    },
  },
  {
    ignores: ['dist/', '.astro/', 'node_modules/', '**/*.d.ts'],
  },
];
