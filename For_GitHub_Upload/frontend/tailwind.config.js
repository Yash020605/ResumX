module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#6366f1',
          600: '#4f46e5',
        },
        secondary: {
          500: '#8b5cf6',
          600: '#7c3aed',
        },
        accent: '#ec4899',
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
        'gradient-page': 'linear-gradient(135deg, #f0f9ff 0%, #faf5ff 100%)',
      },
    },
  },
  plugins: [],
}
