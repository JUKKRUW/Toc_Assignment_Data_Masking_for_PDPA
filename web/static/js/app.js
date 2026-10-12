// App shell: tab routing, theme, language, init.  Owner: M09
import {setLang} from "./i18n.js";
import * as maskPage from "./mask.js";
import * as rulesPage from "./rules.js";
import * as testsPage from "./tests.js";
import * as dfaPage from "./dfa.js";

const PAGES = {mask: maskPage, rules: rulesPage, tests: testsPage, dfa: dfaPage};

// Every page module exports:  init()  (called once)  and  show()  (called each time its tab opens)
// TODO(M09):
//  [ ] tab switching: toggle .active on nav buttons + sections, move nav indicator, call PAGES[tab].show()
//  [ ] theme toggle (light/dark, remember in localStorage, default = prefers-color-scheme)
//  [ ] language segmented control -> setLang()
//  [ ] resize handling (nav indicator, segmented thumbs, auto-height textareas)
for (const p of Object.values(PAGES)) p.init?.();
setLang(localStorage.getItem("pdpa-lang") || "th");
