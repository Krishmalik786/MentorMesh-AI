import Link from "next/link";
import { Logo } from "@/components/logo";
import { ChatPreview } from "@/components/landing/chat-preview";

/**
 * Split-screen auth shell: form on the left, product proof on the right.
 * The right panel collapses away below lg so mobile gets a clean single column.
 */
export function AuthSplit({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="flex flex-col px-6 py-8">
        <Link href="/" className="inline-flex">
          <Logo />
        </Link>
        <div className="flex flex-1 items-center justify-center py-12">
          <div className="w-full max-w-[400px]">{children}</div>
        </div>
      </div>

      <div className="relative hidden flex-col justify-center gap-10 overflow-hidden bg-primary px-12 py-16 text-primary-foreground lg:flex">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 opacity-[0.07]"
          style={{
            backgroundImage:
              "radial-gradient(circle at 1px 1px, currentColor 1px, transparent 0)",
            backgroundSize: "28px 28px",
          }}
        />

        <figure className="relative space-y-4">
          <blockquote className="text-2xl leading-9 font-medium text-balance">
            “It told me my deck claimed traction my repo couldn&apos;t back up. No
            advisor had ever put those two things side by side.”
          </blockquote>
          <figcaption className="text-sm opacity-70">
            Ana Petrova · Co-founder, Loopwise
          </figcaption>
        </figure>

        <div className="relative text-foreground">
          <ChatPreview className="shadow-xl" />
        </div>
      </div>
    </div>
  );
}
