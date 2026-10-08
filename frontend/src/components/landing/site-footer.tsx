import { SITE_LANGUAGES } from "@/lib/languages";

import { ComingSoonLink } from "./coming-soon-link";

type LinkGroup = { heading: string; links: string[] };

/* Five columns; the last one stacks two groups, as on duolingo.com. */
const FOOTER_COLUMNS: LinkGroup[][] = [
  [
    {
      heading: "About us",
      links: ["Courses", "Mission", "Approach", "Efficacy", "Duolingo Handbook", "Research", "Careers", "Store", "Press", "Investors", "Contact us"],
    },
  ],
  [
    {
      heading: "Products",
      links: ["Duolingo", "Duolingo for Schools", "Duolingo English Test", "Podcast", "Duolingo for Business", "Super Duolingo", "Gift Super Duolingo", "Duolingo Max"],
    },
  ],
  [{ heading: "Apps", links: ["Duolingo for Android", "Duolingo for iOS"] }],
  [{ heading: "Help and support", links: ["Duolingo FAQs", "Schools FAQs", "Duolingo English Test FAQs", "Status"] }],
  [
    {
      heading: "Privacy and terms",
      links: ["Community guidelines", "Terms", "Privacy", "Do Not Sell or Share My Personal Information"],
    },
    { heading: "Social", links: ["Blog", "Instagram", "TikTok", "Twitter", "YouTube", "LinkedIn"] },
  ],
];

const linkClasses = "text-left text-[15px] font-bold leading-[22px] text-duo-green-soft hover:text-white";

export function SiteFooter() {
  return (
    <footer className="bg-duo-green">
      <div className="mx-auto max-w-[1020px] px-4 pb-12 pt-8 md:pt-[100px]">
        <div className="grid grid-cols-1 gap-y-10 sm:grid-cols-3 lg:grid-cols-5">
          {FOOTER_COLUMNS.map((groups) => (
            <div key={groups[0].heading} className="flex flex-col gap-10">
              {groups.map(({ heading, links }) => (
                <div key={heading}>
                  <h3 className="text-[19px] font-bold leading-[1.4] text-duo-green-tint">{heading}</h3>
                  <ul className="mt-3 flex flex-col gap-2.5 pr-4">
                    {links.map((link) => (
                      <li key={link}>
                        <ComingSoonLink feature={link} className={linkClasses}>
                          {link}
                        </ComingSoonLink>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          ))}
        </div>

        <div className="mt-14 border-t border-duo-green-soft/60 pt-12">
          <p className="text-[15px] font-bold text-duo-green-tint">Site language:</p>
          <ul className="mt-4 flex flex-wrap gap-x-6 gap-y-3">
            {SITE_LANGUAGES.map(({ id, nativeName }) => (
              <li key={id}>
                <ComingSoonLink feature={`${nativeName} site language`} className="text-[13px] font-bold text-duo-green-soft hover:text-white">
                  {nativeName}
                </ComingSoonLink>
              </li>
            ))}
          </ul>
          <p className="mt-10 text-[13px] font-medium text-duo-green-soft/80">
            A Duolingo clone built for an SDE assignment. Not affiliated with Duolingo, Inc.; brand assets belong to
            their owner.
          </p>
        </div>
      </div>
    </footer>
  );
}
