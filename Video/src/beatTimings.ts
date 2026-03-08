export type BeatTiming = {
  id: string;
  label: string;
  startSec: number;
  durationSec: number;
  swooshOffsetSec?: number;
};

export const beatTimings: BeatTiming[] = [
  // Scene 1 — Browsing Workflow
  { id: "s1_b1", label: "This is my browsing workflow",                   startSec: 0,     durationSec: 3.2 },
  { id: "s1_b2", label: "Open a website",                                 startSec: 3.2,   durationSec: 2.0 },
  { id: "s1_b3", label: "Scan",                                           startSec: 5.2,   durationSec: 1.5 },
  { id: "s1_b4", label: "Choose article",                                 startSec: 6.7,   durationSec: 2.0 },
  { id: "s1_b5", label: "Read",                                           startSec: 8.7,   durationSec: 1.5 },
  { id: "s1_b6", label: "Bookmark",                                       startSec: 10.2,  durationSec: 2.0 },
  { id: "s1_b7", label: "If it has added value",                          startSec: 12.2,  durationSec: 3.0 },
  { id: "s1_b8", label: "Clip with Obsidian",                             startSec: 15.2,  durationSec: 2.5 },
  // Scene 2 — The Problem
  { id: "s2_b1", label: "I have to dig into the bookmarks and clippings", startSec: 17.7,  durationSec: 4.5 },
  { id: "s2_b2", label: "To label",                                       startSec: 22.2,  durationSec: 2.0 },
  { id: "s2_b3", label: "Tag",                                            startSec: 24.2,  durationSec: 1.5 },
  { id: "s2_b4", label: "And organize",                                   startSec: 25.7,  durationSec: 2.5 },
  // Scene 3 — Still Missing
  { id: "s3_b1", label: "And I am still missing valuable information",    startSec: 28.2,  durationSec: 4.0 },
  { id: "s3_b2", label: "Every day",                                      startSec: 32.2,  durationSec: 2.5 },
  // Scene 4 — The Solution
  { id: "s4_b1",  label: "What if I capture first",                       startSec: 34.7,  durationSec: 2.5 },
  { id: "s4_b2",  label: "Catalogue later",                               startSec: 37.2,  durationSec: 2.0 },
  { id: "s4_b3",  label: "Date",                                          startSec: 39.2,  durationSec: 1.5 },
  { id: "s4_b4",  label: "Source",                                        startSec: 40.7,  durationSec: 1.5 },
  { id: "s4_b5",  label: "A folder with a title",                         startSec: 42.2,  durationSec: 2.0 },
  { id: "s4_b6",  label: "Structure before I even decide what matters",   startSec: 44.2,  durationSec: 3.0 },
  { id: "s4_b7",  label: "Markdown files with embedded images",           startSec: 47.2,  durationSec: 2.5 },
  { id: "s4_b8",  label: "Clean data for Obsidian graph",                 startSec: 49.7,  durationSec: 2.5 },
  { id: "s4_b9",  label: "Workflow and input for any LLM",                startSec: 52.2,  durationSec: 2.5 },
  { id: "s4_b10", label: "HTML version with Dark and Light Theme",        startSec: 54.7,  durationSec: 3.0 },
  { id: "s4_b11", label: "Plus Code Coloring",                            startSec: 57.7,  durationSec: 2.0 },
  { id: "s4_b12", label: "Ready to share",                                startSec: 59.7,  durationSec: 2.0 },
  { id: "s4_b13", label: "Quick to Archive",                              startSec: 61.7,  durationSec: 2.0 },
  { id: "s4_b14", label: "Easy to Read",                                  startSec: 63.7,  durationSec: 2.5 },
  // Scene 5 — Product Reveal
  { id: "s5_b1", label: "So I created it",                                startSec: 66.2,  durationSec: 2.5 },
  { id: "s5_b2", label: "Capcat",                                         startSec: 68.7,  durationSec: 2.0, swooshOffsetSec: 0.1 },
  { id: "s5_b3", label: "Capcat?",                                        startSec: 70.7,  durationSec: 3.0, swooshOffsetSec: 0.1 },
  // Scene 6 — Features
  { id: "s6_b1", label: "Command Line mode",                              startSec: 73.7,  durationSec: 3.5 },
  { id: "s6_b2", label: "Interactive menu",                               startSec: 77.2,  durationSec: 5.0 },
  { id: "s6_b3", label: "Bulk RSS fetching",                              startSec: 82.2,  durationSec: 4.0 },
  { id: "s6_b4", label: "Local Markdown storage",                         startSec: 86.2,  durationSec: 2.5 },
  { id: "s6_b5", label: "Offline Accessibility",                          startSec: 88.7,  durationSec: 2.5 },
  // Scene 7 — Outro
  { id: "s7_b1", label: "Archive with confidence",                        startSec: 91.2,  durationSec: 3.0, swooshOffsetSec: 0.3 },
  { id: "s7_b2", label: "Share without limits",                           startSec: 94.2,  durationSec: 3.0 },
  { id: "s7_b3", label: "Free and open source software",                  startSec: 97.2,  durationSec: 3.0 },
  { id: "s7_b4", label: "For developers researchers and tech enthusiasts",startSec: 100.2, durationSec: 4.0 },
  { id: "s7_b5", label: "Capcat.org",                                     startSec: 104.2, durationSec: 3.0 },
  { id: "s7_b6", label: "Defined with natural language processing",       startSec: 107.2, durationSec: 3.0 },
  { id: "s7_b7", label: "Built with large language models",               startSec: 110.2, durationSec: 3.0 },
  { id: "s7_b8", label: "A minimum viable product",                       startSec: 113.2, durationSec: 4.0 },
];

export const TOTAL_DURATION_FRAMES = Math.round(
  (beatTimings[beatTimings.length - 1].startSec +
   beatTimings[beatTimings.length - 1].durationSec) * 30
);
