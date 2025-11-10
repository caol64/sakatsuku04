<script lang="ts">
    import type { Team, TeamsWithRegion, TeamPlayer } from "$lib/models";
    import HStack from "$lib/components/Stack/HStack.svelte";
    import VStack from "$lib/components/Stack/VStack.svelte";
    import { onMount } from "svelte";
    import teamGroupsData from "$locales/team_groups_zh.json";
    import { getGameYear, getRefreshFlag, getSelectedTab, setRefreshFlag } from "$lib/globalState.svelte";
    import { getCooperationType, getGrowType, getPlayerColor, getPosition, getRank, getStyle, getTeamData, getToneType } from "$lib/utils";
    import BPlayerDetails from "./BPlayerDetails.svelte";
    import Close from "$lib/icons/Close.svelte";
    import PlayerIcon from "./PlayerIcon.svelte";


    let treeData: TeamsWithRegion[] = $state([]);
    let openedRegion = $state("");
    let selectedTeam: Team = $state({
        index: 0,
        name: ""
    });
    let teamPlayers: TeamPlayer[] = $state([]);
    let teamFriendly = $state(0);
    let showDrawer = $state(false);
    let playerId = $state(0);
    let age = $state(0);

    function toggleDrawer() {
        showDrawer = !showDrawer;
    }

    function showBPlayer(id: number) {
        playerId = id;
        age = teamPlayers.filter(i => i.id === id)[0].age;
        showDrawer = true;
    }

	function toggleRegion(region: string) {
		openedRegion = openedRegion === region ? "" : region;
	}

    async function selectTeam(team: Team) {
		selectedTeam = team;
        if (window.pywebview?.api?.fetch_team_player) {
            teamPlayers = await window.pywebview.api.fetch_team_player(selectedTeam.index);
            teamFriendly = await window.pywebview.api.fetch_team_friendly(selectedTeam.index);
        } else {
            alert('API 未加载');
        }
	}

    async function featchTeams() {
        treeData = [];
        let index = 0;
        for (let i = 0; i < teamGroupsData.length; i++) {
            const item = teamGroupsData[i];
            const regionName = item[0] as string;
            const max = i + 1 < teamGroupsData.length ? teamGroupsData[i + 1][1] as number : getTeamData().length;
            const teams: Team[] = [];
            for (let i = index; i < max; i++) {
                teams.push({
                    index,
                    name: getTeamData()[index]
                });
                index++;
            }
            treeData.push({
                region: regionName,
                teams: teams
            });
        }
        openedRegion = treeData[0].region;
        selectedTeam = treeData[0].teams[0];
        await selectTeam(selectedTeam);
    }

	onMount(async () => {
        featchTeams();
	});

    $effect(() => {
        if(getRefreshFlag() && getSelectedTab() === "Teams") {
            try {
                featchTeams();
            } finally {
                setRefreshFlag(false);
            }
        }
    });

    async function save() {
        if (window.pywebview?.api?.save_team_friendly) {
            const { message } = await window.pywebview.api.save_team_friendly(selectedTeam.index, teamFriendly);
            if (message === "success") {
                alert("修改成功");
                await selectTeam(selectedTeam);
            } else {
                alert(message);
            }
        } else {
            alert('API 未加载');
        }
    }

</script>

<HStack className="flex-1 overflow-hidden m-2">
    <div class="w-1/5 overflow-y-auto">
        {#each treeData as item}
            <div class="py-0.5 flex items-center gap-x-0.5 w-full">
                <button onclick={() => toggleRegion(item.region)} class="size-6 flex justify-center items-center hover:bg-gray-100 rounded-md">
                    <svg class="size-4 text-gray-800 dark:text-neutral-200" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M5 12h14"></path>
                        {#if openedRegion !== item.region}
                            <path d="M12 5v14"></path>
                        {/if}
                    </svg>
                    <span class="sr-only">Icon</span>
                </button>

                <div class="px-1.5 rounded-md">
                    <span class="text-sm text-gray-800 dark:text-neutral-200">
                        {item.region}
                    </span>
                </div>
            </div>

            {#if openedRegion === item.region}
                <div class="">
                    {#each item.teams as team}
                        <div class="ps-7 relative before:absolute before:top-0 before:start-3 before:w-0.5 before:-ms-px before:h-full before:bg-gray-100 dark:before:bg-neutral-700">
                            <button onclick={() => selectTeam(team)} class={ selectedTeam.index === team.index ? "activate px-1.5 rounded-md cursor-pointer hover:bg-gray-100" : "px-1.5 rounded-md cursor-pointer hover:bg-gray-100" }>
                                <span class="text-sm text-gray-800 dark:text-neutral-200">
                                    {team.name}
                                </span>
                            </button>
                        </div>
                    {/each}
                </div>
            {/if}
        {/each}
    </div>

    <VStack className="relative overflow-x-auto grow mx-2">
        <HStack className="items-center mb-1">
            <label for="gameDifficulty" class="w-16">友好度</label>
            <span class="text-sm w-16">{ teamFriendly }</span>
            <input id="gameDifficulty" type="range" min="0" max="255" bind:value={ teamFriendly } class="w-52 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700">
            <button onclick={save} class="w-18 h-8 rounded-md cursor-pointer mx-2 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium text-sm text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
                保存
            </button>
        </HStack>
        <table class="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
            <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
                <tr>
                    <th class="w-48">球员</th>
                    <th>年龄</th>
                    <th>位置</th>
                    <th>等级</th>
                    <th class="w-40">风格</th>
                    <th>连携</th>
                    <th class="w-24">性格</th>
                    <th class="w-16">身体</th>
                    <th class="w-16">技术</th>
                    <th class="w-16">头脑</th>
                </tr>
            </thead>
            <tbody>
                {#each teamPlayers as item}
                    <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 border-gray-200">
                        <th scope="row" class="px-2 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white" style={`background-image: linear-gradient(to right, transparent 66%, ${getPlayerColor(item.pos)} 100%)`}>
                            <span class="flex items-center justify-between w-full">
                                <button onclick={() => { showBPlayer(item.id) }} class="cursor-pointer select-text">
                                    {item.name}
                                </button>
                                <PlayerIcon teamPlayer={item} />
                            </span>
                        </th>
                        <td>{item.age}</td>
                        <td>{getPosition(item.pos)}</td>
                        <td>{getRank(item.rank)}</td>
                        <td>{getStyle(item.style)}</td>
                        <td>{getCooperationType(item.cooperationType)}</td>
                        <td>{getToneType(item.toneType)}</td>
                        <td>{getGrowType(item.growTypePhy)}</td>
                        <td>{getGrowType(item.growTypeTec)}</td>
                        <td>{getGrowType(item.growTypeSys)}</td>
                    </tr>
                {/each}
            </tbody>
        </table>
    </VStack>

    <div class="fixed top-0 left-0 h-full w-full bg-white dark:bg-gray-800 shadow-lg transition-transform duration-300 z-50"
        class:translate-x-0={showDrawer}
        class:translate-x-full={!showDrawer}>
        <HStack className="flex-1 h-full overflow-hidden m-2.5">
            <VStack className="w-1/5">
                <button onclick={toggleDrawer} class="cursor-pointer">
                    <Close />
                </button>
            </VStack>
            <BPlayerDetails selectedPlayer={playerId} selectedYear={getGameYear()} age={age} />
        </HStack>
    </div>
</HStack>

<style lang="postcss">
    @reference "tailwindcss";
    .activate {
        @apply bg-gray-100  dark:bg-gray-600;
    }
    th {
        @apply px-1 py-1;
    }
    td {
        @apply px-1 py-1;
    }
</style>
