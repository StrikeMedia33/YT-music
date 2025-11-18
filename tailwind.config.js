/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // Enable class-based dark mode
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontSize: {
        // Display (Hero Headlines)
        'display-lg': ['3.75rem', { lineHeight: '1.1', letterSpacing: '-0.02em', fontWeight: '700' }], // 60px
        'display-md': ['3rem', { lineHeight: '1.15', letterSpacing: '-0.02em', fontWeight: '700' }],     // 48px
        'display-sm': ['2.25rem', { lineHeight: '1.2', letterSpacing: '-0.01em', fontWeight: '600' }],   // 36px

        // Headings (Page/Section Headers)
        'heading-lg': ['1.875rem', { lineHeight: '1.3', fontWeight: '600' }], // 30px - Page headers
        'heading-md': ['1.5rem', { lineHeight: '1.35', fontWeight: '600' }],   // 24px - Section headers
        'heading-sm': ['1.25rem', { lineHeight: '1.4', fontWeight: '600' }],   // 20px - Card headers

        // Body Text
        'body-lg': ['1.125rem', { lineHeight: '1.75', fontWeight: '400' }],    // 18px
        'body-md': ['1rem', { lineHeight: '1.6', fontWeight: '400' }],         // 16px - Default
        'body-sm': ['0.875rem', { lineHeight: '1.5', fontWeight: '400' }],     // 14px

        // UI Elements
        'label-lg': ['0.875rem', { lineHeight: '1.25', fontWeight: '500' }],   // 14px - Form labels
        'label-sm': ['0.75rem', { lineHeight: '1.25', fontWeight: '500' }],    // 12px - Small labels
        'caption': ['0.75rem', { lineHeight: '1.5', fontWeight: '400' }],      // 12px - Help text
      },
      spacing: {
        // Add consistent spacing scale
        '18': '4.5rem',
        '88': '22rem',
      },
    },
  },
  plugins: [],
}
