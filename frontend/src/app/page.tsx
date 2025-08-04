import Image from "next/image";
import { ConfigDemo } from "./components/EnhancedConfigDemo";

export default function Home() {
  return (
    <div className="font-sans grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start max-w-4xl">
        <Image
          className="dark:invert"
          src="/next.svg"
          alt="Next.js logo"
          width={180}
          height={38}
          priority
        />

        {/* Configuration Demo Component */}
        <ConfigDemo />

        <ol className="font-mono list-inside list-decimal text-sm/6 text-center sm:text-left">
          <li className="mb-2 tracking-[-.01em]">
            The configuration system is now integrated with{" "}
            <code className="bg-black/[.05] dark:bg-white/[.06] font-mono font-semibold px-1 py-0.5 rounded">
              backend API endpoints
            </code>
            .
          </li>
          <li className="tracking-[-.01em]">
            Dynamic branding, features, and settings are loaded from the
            backend.
          </li>
        </ol>

        <div className="flex gap-4 items-center flex-col sm:flex-row">
          <a
            className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-foreground text-background gap-2 hover:bg-[#383838] dark:hover:bg-[#ccc] font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 sm:w-auto"
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Image
              className="dark:invert"
              src="/globe.svg"
              alt="API docs"
              width={20}
              height={20}
            />
            API Documentation
          </a>
          <a
            className="rounded-full border border-solid border-black/[.08] dark:border-white/[.145] transition-colors flex items-center justify-center hover:bg-[#f2f2f2] dark:hover:bg-[#1a1a1a] hover:border-transparent font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 w-full sm:w-auto md:w-[180px]"
            href="/api-test"
            rel="noopener noreferrer"
          >
            Test API Endpoints
          </a>
        </div>
      </main>
      <footer className="row-start-3 flex gap-[24px] flex-wrap items-center justify-center">
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="http://localhost:8000/api/v1/config"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/file.svg"
            alt="Config icon"
            width={16}
            height={16}
          />
          View Config API
        </a>
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="http://localhost:8000/api/v1/config/branding"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/window.svg"
            alt="Branding icon"
            width={16}
            height={16}
          />
          Branding Config
        </a>
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="http://localhost:8000/api/v1/config/features"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/globe.svg"
            alt="Features icon"
            width={16}
            height={16}
          />
          Feature Flags
        </a>
      </footer>
    </div>
  );
}
