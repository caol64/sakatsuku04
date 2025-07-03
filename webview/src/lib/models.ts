export interface Response {
    message: string;
}

export interface Club {
    year: number;
    month: number;
    date: number;
    day: number;
    fundsHigh: number;
    fundsLow: number;
    managerName: string;
    clubName: string;
    difficulty: number;
}

export const defaultClubData = {
    year: 0,
    month: 0,
    date: 0,
    day: 0,
    fundsHigh: 0,
    fundsLow: 0,
    managerName: "",
    clubName: "",
    difficulty: 0,
}

export interface Team {
    index: number;
    name: string;
    friendly: number;
}

export interface TeamsWithRegion {
    region: string;
    teams: Team[];
}

export interface TeamPlayer {
    id: number;
    age: number;
    abilityGraph: number;
    number: number;
    name: string;
    rank: string;
    pos: string;
    cooperationType: string;
    toneType: string;
    growTypePhy: string;
    growTypeTec: string;
    growTypeSys: string;
}

export interface MyPlayer {
    index: number;
    id: number;
    age: number;
    number: number;
    name: string;
    born: number;
    abroadTimes: number;
    height: number;
    foot: number;
    rank: number;
    pos: number;
    growTypePhy: number;
    growTypeTec: number;
    growTypeSys: number;
    toneType: number;
    cooperationType: number;
    style: number;
    abilities: MyPlayerAbility[]
}

export interface MyPlayerAbility {
    index: number;
    current: number;
    currentMax: number;
    max: number;
    currentPercent: number;
    currentMaxPercent: number;
    maxPercent: number;
}
