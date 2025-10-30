// eslint.config.js
import js from '@eslint/js';
import globals from 'globals';
import pluginVue from 'eslint-plugin-vue';
import { defineConfig } from 'eslint/config';
import eslintConfigPrettier from 'eslint-config-prettier/flat'; // avoid conflicts between ESLint & Prettier

export default defineConfig([
  {
    files: ['**/*.{js,mjs,cjs,vue}'],
    languageOptions: { globals: globals.browser },
    plugins: { js },
    extends: ['js/recommended'],
  },
  pluginVue.configs['flat/essential'],
  eslintConfigPrettier, // disables ESLint rules that conflict with Prettier
]);
