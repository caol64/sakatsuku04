export interface Club {
    year?: number;
    month?: number;
    date?: number;
    day?: number;
    fundsHigh?: number;
    fundsLow?: number;
    managerName?: string;
    clubName?: string;
    difficulty?: number;
    seed?: number;
}

export interface Team {
    index: number;
    name: string;
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
    rank: number;
    pos: number;
    cooperationType: number;
    toneType: number;
    growTypePhy: number;
    growTypeTec: number;
    growTypeSys: number;
    isAlbum: boolean;
    teamIndex: number;
}

export interface MyTeamPlayer {
    id: number;
    name: string;
    pos: number;
    isAlbum: boolean;
}

export interface MyPlayer {
    index?: number;
    id?: number;
    age?: number;
    number?: number;
    name?: string;
    born?: number;
    abroadTimes?: number;
    height?: number;
    foot?: number;
    rank?: number;
    pos?: number;
    growTypePhy?: number;
    growTypeTec?: number;
    growTypeSys?: number;
    toneType?: number;
    cooperationType?: number;
    style?: number;
    abilities: MyPlayerAbility[];
    desire?: number;
    pride?: number;
    ambition?: number;
    patient?: number;
    persistence?: number;
    jlFactor?: number;
    hexagon: number[];
    odc: number[];
    abilEval?: number;
    spComment?: string;
    salaryHigh?: number;
    salaryLow?: number;
    offerYearsPassed?: number;
    offerYearsTotal?: number;
}

export interface MyPlayerAbility {
    index: number;
    current: number;
    currentMax: number;
    max: number;
}
