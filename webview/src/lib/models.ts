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
    seed: number;
    teamStatus: number;
}

export type EmptyClub = Partial<Club>;

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
    style: number;
    growTypePhy: number;
    growTypeTec: number;
    growTypeSys: number;
    albumType: number;
    teamIndex: number;
    scouts?: string[];
    bringAbroads: number[];
}

export interface MyTeamPlayer {
    id: number;
    name: string;
    pos: number;
    isAlbum: boolean;
    scouts?: string[];
    bringAbroads?: number[];
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
    waveType?: number;
    hexagon: number[];
    odc: number[];
    abilEval?: number;
    growEval?: number;
    aposEval?: number[];
    maxAbilEval?: number;
    spComment?: string;
    baddenPlayers?: string[];
    salaryHigh?: number;
    salaryLow?: number;
    offerYearsPassed?: number;
    offerYearsTotal?: number;
    phyGrows?: number[];
    tecGrows?: number[];
    sysGrows?: number[];
    power?: number;
    moti?: number;
    kan?: number;
    superSub?: number;
    wildType?: number;
    weakType?: number;
    tiredType?: number;
    pop?: number;
    comp?: number[];
    tired?: number;
    status?: number;
    condition?: number;
    gp?: number;
}

export interface MyPlayerAbility {
    index: number;
    current: number;
    currentMax: number;
    max: number;
}

export interface MyTown {
    living?: number;
    economy?: number;
    sports?: number;
    env?: number;
    population?: number;
    price?: number;
    trafficLevel?: number;
    soccerPop?: number;
    soccerLevel?: number;
    townType?: number;
}

export interface Scout {
    id: number;
    name: string;
    born?: number;
    age?: number;
    offerYears?: number;
    contractYears?: number;
    salaryHigh?: number;
    salaryLow?: number;
    rank?: number;
    exclusivePlayers?: Search[];
    simiExclusivePlayers?: Search[];
    abilities: number[];
    hasExclusive: boolean;
    hexagon?: number[];
    aposEval?: number[];
    nati1?: number;
    nati2?: number;
    eval?: string;
}

export interface Search {
    name?: string;
    pos?: number;
    age?: number;
    country?: number;
    rank?: number;
    cooperation?: number;
    tone?: number;
    teamId?: number;
}

export interface AbroadCond {
    id: number;
    cond: number[] | string[];
}

export interface Abroad {
    id: number;
    isEnabled: boolean;
    cond?: AbroadCond;
    abrUp: number[];
    abrUprate: number[];
    abrDays: number;
}

export interface BPlayer {
    id?: number;
    name?: string;
    born?: number;
    pos?: number;
    age?: number;
    rank?: number;
    toneType?: number;
    cooperationType?: number;
    waveType?: number;
    growTypePhy?: number;
    growTypeTec?: number;
    growTypeSys?: number;
    abilities: number[];
    height?: number;
    style?: number;
    hexagon: number[];
    odc: number[];
    abilEval?: number;
    aposEval?: number[];
    spComment?: string;
    baddenPlayers?: string[];
    phyGrows?: number[];
    tecGrows?: number[];
    sysGrows?: number[];
    foot?: number;
    desire?: number;
    pride?: number;
    ambition?: number;
    patient?: number;
    persistence?: number;
    superSub?: number;
    wildType?: number;
    weakType?: number;
    tiredType?: number;
    pop?: number;
    unlockYear?: number;
    signingDifficulty?: number;
    growEval?: number;
    gp?: number;
}

export interface Coach {
    id: number;
    name: string;
    born?: number;
    age?: number;
    offerYears?: number;
    contractYears?: number;
    salaryHigh?: number;
    salaryLow?: number;
    rank?: number;
    spPrac1?: number;
    spPrac2?: number;
    bringAbroads: AbrStatus[];
    abilities: number[];
    spSkill?: number;
    isBringAbroad?: boolean;
    isTopRank?: boolean;
    eval?: string;
    hexagon?: number[];
    activatePlan?: number;
    trainingPlan?: number;
    trainingStrength?: number;
    styles?: number[];
}

export interface BScout {
    id?: number;
    name?: string;
    born?: number;
    abilities: number[];
    hexagon: number[];
    aposEval?: number[];
    nati1?: number;
    nati2?: number;
    age?: number;
    rank?: number;
    salaryHigh?: number;
    salaryLow?: number;
    exclusivePlayers?: string[];
    simiExclusivePlayers?: string[];
    signingDifficulty?: number;
    eval?: string;
    ambition?: number;
    persistence?: number;
}

export interface BCoach {
    id?: number;
    name?: string;
    born?: number;
    abilities: number[];
    hexagon: number[];
    age?: number;
    rank?: number;
    salaryHigh?: number;
    salaryLow?: number;
    signingDifficulty?: number;
    eval?: string;
    styles?: number[];
    coachType?: number;
    desire?: number;
    ambition?: number;
    persistence?: number;
    activatePlan?: number;
    trainingPlan?: number;
    trainingStrength?: number;
    acSpPractice1?: number;
    acSpPractice2?: number;
    spSkill?: number;
    coachTypeCnv?: number;
    bringAbroads?: AbrStatus[];
}

export interface AbrStatus {
    id: number;
    type: number;
    isEnabled: boolean;
}

export interface Sponsors {
    id: number;
    contractYears: string;
    offerYears: number;
    amountHigh: number;
    amountLow: number;
    bringAbroads: AbrStatus[];
    combo?: SponsorCombo[];
}

export interface SponsorCombo {
    parentId: number;
    subsidiaryIds: number[];
    type: number;
}

export interface Trophy {
    winTimes: number;
    entryTimes: number;
    index?: number;
}
