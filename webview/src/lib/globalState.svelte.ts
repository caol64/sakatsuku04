import { defaultClubData, type Club } from "./models";

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

let clubData: Club = $state(defaultClubData);

export function getClubData(): Club {
    return clubData;
}

export function setClubData(data: Club) {
    clubData = data;
}

// -------selectedTab-------

export type Tab = "Club" | "Players" | "Teams" | "Scouts";
export const allTabs: Tab[] = ["Club", "Players", "Teams"];

let selectedTab: Tab = $state("Club");

export function getSelectedTab() : Tab {
    return selectedTab;
}

export function setSelectedTab(value: Tab) {
    selectedTab = value;
}
