# Next.js + shadcn/ui Boilerplate

A modern, production-ready boilerplate for building React applications with Next.js 15 and shadcn/ui components. This starter template provides a solid foundation for future projects with best practices and essential tooling pre-configured.

## ✨ Features

- **Next.js 15** - Latest version with App Router and React Server Components
- **shadcn/ui** - Beautiful, accessible UI components built with Radix UI and Tailwind CSS
- **TypeScript** - Full type safety throughout the project
- **Tailwind CSS v4** - Utility-first CSS framework with modern features
- **ESLint** - Code linting with Next.js recommended configuration
- **Turbopack** - Ultra-fast bundler for development (via `--turbopack` flag)
- **Modern Icons** - Lucide React icons integrated
- **Class Variance Authority** - For creating type-safe component variants
- **Utility Functions** - Pre-configured with `clsx` and `tailwind-merge`

## 🚀 Quick Start

1. **Clone or use this template**

   ```bash
   git clone [your-repo-url]
   cd nextjs_shadcn_boilerplate
   ```

2. **Install dependencies**

   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

3. **Start the development server**

   ```bash
   npm run dev
   ```

4. **Open your browser**

   Navigate to [http://localhost:3000](http://localhost:3000) to see your application.

## 📁 Project Structure

```text
├── app/                 # App Router directory (Next.js 13+)
│   ├── globals.css     # Global styles with Tailwind directives
│   ├── layout.tsx      # Root layout component
│   └── page.tsx        # Home page component
├── components/         # Reusable React components
│   └── ui/            # shadcn/ui components (auto-generated)
├── lib/               # Utility functions and configurations
│   └── utils.ts       # Common utility functions (cn, etc.)
├── public/            # Static assets
├── components.json    # shadcn/ui configuration
├── tailwind.config.js # Tailwind CSS configuration
└── tsconfig.json      # TypeScript configuration
```

## 🎨 Adding Components

This boilerplate comes with shadcn/ui pre-configured. You can add new components using:

```bash
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add card
# ... and many more
```

Components will be automatically added to the `components/ui/` directory with proper TypeScript definitions.

## 🛠 Available Scripts

- `npm run dev` - Start development server with Turbopack
- `npm run build` - Build the application for production
- `npm run start` - Start the production server
- `npm run lint` - Run ESLint for code linting

## 🔧 Configuration

### shadcn/ui Configuration

- **Style**: New York
- **Base Color**: Neutral
- **CSS Variables**: Enabled
- **Icon Library**: Lucide React
- **RSC**: Enabled (React Server Components)

### Tailwind CSS

- Version 4 with modern features
- CSS variables for theming
- Configured for shadcn/ui components

## 📚 Tech Stack

- **Framework**: Next.js 15
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui
- **Icons**: Lucide React
- **Development**: Turbopack, ESLint

## 🚀 Deployment

This project is ready to be deployed on platforms like:

- **Vercel** (recommended for Next.js)
- **Netlify**
- **Railway**
- **Docker** containers

### Deploy on Vercel

1. Push your code to a Git repository
2. Import your project on [Vercel](https://vercel.com)
3. Your app will be automatically deployed

## 📖 Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**Ready to build something amazing!** 🎉

This boilerplate provides everything you need to start your next project with modern web development practices and tools.
