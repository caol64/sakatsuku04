import { type Club } from "./models";

// -------mode-------

export type ModeState = "saveEditor" | "memoryEditor" | "";

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

// -------clubData-------

let clubData: Club = $state({});

export function getClubData(): Club {
    return clubData;
}

export function setClubData(data: Club) {
    clubData = data;
}

// -------selectedTab-------

export type Tab = "Game" | "Players" | "Teams" | "Search" | "Scouts" | "Town" | "Album";
export const allTabs: Tab[] = ["Game", "Players", "Teams", "Search", "Scouts", "Town", "Album"];

let selectedTab: Tab = $state("Game");

export function getSelectedTab() : Tab {
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

export function getIsLoading() {
    return isLoading;
}

export function setIsLoading(value: boolean) {
    isLoading = value;
}

// -------refreshFlag-------

let refreshFlag = $state(false);

export function getRefreshFlag() {
    return refreshFlag;
}

export function setRefreshFlag(value: boolean) {
    refreshFlag = value;
}
