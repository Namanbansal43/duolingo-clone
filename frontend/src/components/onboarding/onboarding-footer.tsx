import type { ReactNode } from "react";

/**
 * The bar along the bottom of each onboarding screen, holding its CONTINUE button.
 * The extra 4px of bottom padding leaves room for the button's ledge, which is a shadow outside its box.
 */
export function OnboardingFooter({ children }: { children: ReactNode }) {
  return (
    <footer className="border-t-2 border-line">
      <div className="mx-auto flex max-w-[1140px] justify-end px-4 pt-4 pb-5 sm:px-6 sm:pt-12 sm:pb-[52px] [&>*]:w-full sm:[&>*]:w-auto">
        {children}
      </div>
    </footer>
  );
}
