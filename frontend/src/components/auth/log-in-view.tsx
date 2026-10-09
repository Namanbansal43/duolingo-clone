"use client";

import { X } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { toast } from "sonner";

import { Button, buttonClasses } from "@/components/ui/button";
import { signIn } from "@/lib/api/endpoints";
import { cn } from "@/lib/cn";

const FIELD =
  "h-12 w-full rounded-2xl border-2 border-line bg-snow px-[14px] text-[20px] leading-7 font-medium text-ink outline-none placeholder:text-ink-faint";

/**
 * /log-in, laid out like duolingo.com's log-in screen. The brief assumes one logged-in learner, so there
 * is a single demo account and no password: LOG IN signs this browser in as the demo learner (leaving the
 * guest from "Get started", if it was one) and opens /learn. Duolingo's Google, Facebook and Apple buttons
 * are left out, as they would do nothing here.
 */
export function LogInView() {
  const router = useRouter();
  const [signingIn, setSigningIn] = useState(false);

  const logIn = async (event: FormEvent) => {
    event.preventDefault();
    setSigningIn(true);
    try {
      await signIn();
      router.push("/learn");
    } catch (error) {
      toast(error instanceof Error ? error.message : "Couldn't log in. Please try again.");
      setSigningIn(false);
    }
  };

  return (
    <div className="min-h-svh bg-page px-4 pb-12">
      <header className="flex h-20 items-center justify-between sm:h-[110px]">
        <Link
          href="/"
          aria-label="Close"
          className="rounded-md p-1 text-ink-faint outline-none hover:brightness-75 focus-visible:ring-4 focus-visible:ring-duo-blue-border sm:ml-2.5"
        >
          <X className="size-6" strokeWidth={3} />
        </Link>
        <Link
          href="/welcome"
          className={buttonClasses({
            variant: "outline",
            className: "h-[50px] rounded-2xl px-4 text-[15px] tracking-[0.8px] sm:mr-2.5",
          })}
        >
          Sign up
        </Link>
      </header>

      <main className="mx-auto w-full max-w-[375px]">
        <h1 className="text-center text-[26px] leading-10 font-bold text-ink-strong sm:-mt-[22px]">Log in</h1>
        <form onSubmit={(event) => void logIn(event)} className="mt-6">
          <label className="sr-only" htmlFor="username">
            Username
          </label>
          <input id="username" value="alex" readOnly className={FIELD} />
          <label className="sr-only" htmlFor="password">
            Password
          </label>
          <input
            id="password"
            type="password"
            disabled
            placeholder="No password needed for the demo"
            className={cn(FIELD, "mt-3 text-[17px]")}
          />
          <Button
            type="submit"
            variant="secondary"
            fullWidth
            disabled={signingIn}
            className="mt-6 h-[50px] rounded-2xl text-[15px] tracking-[0.8px]"
          >
            Log in
          </Button>
        </form>
        <p className="mt-8 text-center text-[14px] leading-5 font-medium text-ink-faint">
          This demo has one account, <strong className="font-bold">Alex</strong>. Logging in continues with
          Alex&rsquo;s progress; anything done after &ldquo;Get started&rdquo; stays with that guest.
        </p>
      </main>
    </div>
  );
}
