import { defaultBaseData, type Base, type SaveEntry } from "./models";

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

let saveList: SaveEntry[] = $state([]);

export function getSaveList(): SaveEntry[] {
    return saveList;
}

export function setSaveList(value: SaveEntry[]) {
    saveList = value;
}

// -------baseData-------

let baseData: Base = $state(defaultBaseData);

export function getBaseData(): Base {
    return baseData;
}

export function setBaseData(data: Base) {
    baseData = data;
}

// -------selectedTab-------

export type Tab = "Base" | "My Team" | "Other Teams" | "Scouts";
export const allTabs: Tab[] = ["Base", "My Team", "Other Teams", "Scouts"];

let selectedTab: Tab = $state("Base");

export function getSelectedTab() : Tab {
    return selectedTab;
}

export function setSelectedTab(value: Tab) {
    selectedTab = value;
}
