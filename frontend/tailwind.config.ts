import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        border: '#E5E7EB',
        panel: '#FFFFFF',
        canvas: '#F9FAFB'
      }
    }
  },
  plugins: []
};

export default config;
