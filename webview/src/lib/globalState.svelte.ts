// -------locale-------

export type Locale = "zh" | "jp";

let locale: Locale = $state("zh");

export function getLocale() : Locale {
    return locale;
}

export function setLocale(value: Locale) {
    locale = value;
}

// -------mode-------

export type ModeState = "saveEditor" | "memoryEditor" | "" | "bPlayerView" | "bScoutView" | "bCoachView";

let modeState: ModeState = $state("");

export function getModeState() : ModeState {
    return modeState;
}

export function setModeState(value: ModeState) {
    modeState = value;
}

// -------saveList-------

let saveList: string[] = $state([]);

export function getSaveList(): string[] {
    return saveList;
}

export function setSaveList(value: string[]) {
    saveList = value;
}

// -------selectedGame-------

let selectedGame = $state("");

export function getSelectedGame(): string {
    return selectedGame;
}

export function setSelectedGame(value: string) {
    selectedGame = value;
}

// -------gameVersion-------

export let gameVersion = "zh";

export function setGameVersion(value: number) {
    gameVersion = value === 0 ? "jp" : "zh";
}

// -------gameYear-------

let gameYear = $state(1);

export function getGameYear(): number {
    return gameYear;
}

export function setGameYear(value: number) {
    gameYear = value;
}

// -------selectedTab-------

export const allTabs = [
    "Game",
    "Players",
    "Teams",
    "Search",
    "Scouts",
    "Coaches",
    "Town",
    "Sponsors",
    "Album",
    "Abroad"
] as const;

export type Tab = typeof allTabs[number];

let selectedTab: Tab = $state("Game");

export function getSelectedTab(): Tab {
    return selectedTab;
}

export function setSelectedTab(value: Tab) {
    selectedTab = value;
}

export function setDefaultTab() {
    selectedTab = "Game";
}

// -------isLoading-------

let isLoading = $state(false);

export function getIsLoading(): boolean {
    return isLoading;
}

export function setIsLoading(value: boolean) {
    isLoading = value;
}

// -------refreshFlag-------

let refreshFlag = $state(false);

export function getRefreshFlag(): boolean {
    return refreshFlag;
}

export function setRefreshFlag(value: boolean) {
    refreshFlag = value;
}
