import js from '@eslint/js';
import globals from 'globals';
import pluginVue from 'eslint-plugin-vue';
import { defineConfig } from 'eslint/config';
import eslintConfigPrettier from 'eslint-config-prettier/flat'; // Import Prettier configuration for ESLint

export default defineConfig([
  {
    files: ['**/*.{js,mjs,cjs,vue}'],
    plugins: { js },
    extends: ['js/recommended'],
    languageOptions: { globals: globals.browser },
  },
  pluginVue.configs['flat/essential'],
  eslintConfigPrettier, // Add the Prettier configuration here to avoid conflicts between ESLint and Prettier
]);
