module.exports = {
    purge: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
    darkMode: false,
    theme: {
      extend: {
        outline: {
            grey: '2px solid #ddd',
          }, 
          fontFamily: {
            sans: ['Helvetica', 'Arial', 'sans-serif']
          },
          fontSize: {
            '3xl': '2rem'
          },
          boxShadow: {
            button: '0 1px 3px 0 rgb(60 64 67 / 30%), 0 4px 8px 3px rgb(60 64 67 / 15%)',
            navbar: '0 1px 2px 0 rgba(60,64,67,0.3),0 2px 6px 2px rgba(60,64,67,0.15)',
            box: '0 1px 2px 0 rgba(60,64,67,.3),0 2px 6px 2px rgba(60,64,67,.15)',
            hover: '0 8px 24px 0px rgba(0,0,0,0.5)',
            outline: '0 0 0 3px rgba(71, 92, 170, 0.7)'
          },
          cursor: {
            grab: 'grab',
          },
          colors: {
            label: '#4f5a65',
            green: '#289b6a',
            blue: '#475caa',
            'semi-transparent': 'hsla(0, 0%, 4%, .2)',
            'semi-transparent-darken': 'hsla(0, 0%, 4%, .3)',
            loading: 'rgba(0, 0, 0, 0.5)',
          },
          minHeight: {
            '200-px': '200px',
            banner: 'calc(100vh - 104px)', // rest the footer
            'banner-header': 'calc(100vh - 104px - 56px)' // rest the footer and the header
          },
          zIndex: {
            1000: '1000',
          },
          inset: {
            41: '41%'
          },
          spacing: {
            68: '17rem',
            82: '20rem',
            96: '24rem',
            104: '28rem',
          },
          gridTemplateColumns: {
            program: 'minmax(100px, auto) 1fr',
            deployments: 'auto repeat(3, 1fr) 50px',
            'form-2': '0.5fr 1fr',
            'form-4': '0.5fr 1fr 0.5fr 1fr',
          }
        },
    },
    variants: {
        fontSize: ['responsive', 'hover', 'focus'],
      },
    plugins: [],
  }
