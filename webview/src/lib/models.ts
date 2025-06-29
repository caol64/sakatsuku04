export interface Response {
    message: string;
}

export interface SaveEntry {
    name: string;
}

export interface Base {
    year: number;
    month: number;
    date: number;
    day: number;
    fundHeigh: number;
    fundLow: number;
    managerName: string;
    clubName: string;
    difficulty: number;
}

export const defaultBaseData = {
    year: 0,
    month: 0,
    date: 0,
    day: 0,
    fundHeigh: 0,
    fundLow: 0,
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
    teamWork: string;
    toneType: string;
    growTypePhy: string;
    growTypeTech: string;
    growTypeSys: string;
}

export interface MyPlayer {
    index: number;
    id: number;
    age: number;
    number: number;
    name: string;
}
