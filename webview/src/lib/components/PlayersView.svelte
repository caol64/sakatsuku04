<script lang="ts">
    import type { MyPlayer, MyTeamPlayer } from "$lib/models";
    import { onMount } from "svelte";
    import HStack from "./Stack/HStack.svelte";
    import RadarChart from "./RadarChart.svelte";
    import StatusBars from "./StatusBars.svelte";
    import PositionGrid from "./PositionGrid.svelte";
    import VStack from "./Stack/VStack.svelte";
    import Tooltip from "./Tooltip.svelte";
    import Modal from "./Modal.svelte";
    import PlayersEditor from "./PlayersEditor.svelte";
    import { getCooperationType, getGrowType, getPosition, getRank, getRegion, getStyle, getToneType, preferFoot, sortedAbilities } from "$lib/utils";
    import { getRefreshFlag, getSelectedTab, setRefreshFlag } from "$lib/globalState.svelte";

    let myPlayers: MyTeamPlayer[] = $state([]);
    let selectedPlayer = $state(0);
    let myPlayer: MyPlayer = $state({ abilities: [] });
    let stats = [0.9, 0.7, 0.6, 0.5, 0.8, 0.4];
    let bars = [0.9, 0.5, 0.7];

    let abilityPairs = $derived(
        sortedAbilities.map((label, i) => ({
            label,
            value: myPlayer?.abilities?.[i] ?? {
                index: 0,
                current: 0,
                currentMax: 0,
                max: 0,
                currentPercent: 0,
                currentMaxPercent: 0,
                maxPercent: 0
            }
        }))
    );

    function toPercentString(value: number): string {
        if (value === undefined) {
            return "";
        }
        const percent = Math.round(value * 100);
        return `${percent}%`;
    }

    async function fetchMyPlayer(id: number) {
        if (selectedPlayer !== id) {
            selectedPlayer = id;
            if (window.pywebview?.api?.fetch_my_player) {
                myPlayer = await window.pywebview.api.fetch_my_player(id);
            } else {
                alert('API 未加载');
            }
        }
    }

    async function fetchMyTeam() {
        if (window.pywebview?.api?.fetch_my_team) {
            myPlayers = await window.pywebview.api.fetch_my_team();
            if (myPlayers) {
                selectedPlayer = myPlayers[0].id;
                myPlayer = await window.pywebview.api.fetch_my_player(selectedPlayer);
            }
        } else {
            alert('API 未加载');
        }
    }

    $effect(() => {
        if(getRefreshFlag() && getSelectedTab() === "Players") {
            try {
                fetchMyTeam();
            } finally {
                setRefreshFlag(false);
            }
        }
    });

    onMount(async () => {
        fetchMyTeam();
	});

    let isModalOpen = $state(false);

    function openModal() {
        isModalOpen = true;
    }

    function closeModal() {
        isModalOpen = false;
    }

    async function onSaveSuccess() {
        closeModal();
        if (window.pywebview?.api?.fetch_my_player) {
            myPlayer = await window.pywebview.api.fetch_my_player(selectedPlayer);
        } else {
            alert('API 未加载');
        }
    }
</script>

<HStack className="flex-1 overflow-hidden m-2.5">
    <VStack className="w-1/5 mr-1">
        <HStack className="space-x-4 mb-2 mx-2">
            <button class="badges">一线队</button>
            <button class="badges">青年队</button>
            <button class="badges">转会市场</button>
        </HStack>
        <div class="sidebar">
            {#each myPlayers as item}
                <button onclick={() => fetchMyPlayer(item.id)} class={ selectedPlayer === item.id ? "activate" : "" }>
                    { item.name }
                </button>
            {/each}
        </div>
    </VStack>

    <VStack className="w-1/5 mx-1">
        <div class="border border-gray-200 dark:border-gray-600 rounded-md p-4 space-y-2 bg-gray-50 dark:bg-gray-700">
            <p>姓名<span>{myPlayer?.name}</span></p>
            <p>年龄<span>{myPlayer?.age}</span></p>
            <p>号码<span>{myPlayer?.number}</span></p>
            <p>留学次数<span>{myPlayer?.abroadTimes}</span></p>
            <p>出生地<span>{getRegion(myPlayer?.born)}</span></p>
            <p>惯用脚<span>{preferFoot(myPlayer?.foot)}</span></p>
            <p>身高<span>{myPlayer?.height}</span></p>
            <p>位置<span>{getPosition(myPlayer?.pos)}</span></p>
            <p>风格<span>{getStyle(myPlayer?.style)}</span></p>
            <p>对战评价<span>{getRank(myPlayer?.rank)}</span></p>
            <p>连携<span>{getCooperationType(myPlayer?.cooperationType)}</span></p>
            <p>性格<span>{getToneType(myPlayer?.toneType)}</span></p>
            <p>成长类型</p>
            <div class="pl-4">
                <p>身体<span>{getGrowType(myPlayer?.growTypePhy)}</span></p>
                <p>技术<span>{getGrowType(myPlayer?.growTypeTec)}</span></p>
                <p>头脑<span>{getGrowType(myPlayer?.growTypeSys)}</span></p>
            </div>
            <p>隐藏属性</p>
            <div class="pl-4">
                <p>逆境<span>{myPlayer?.desire}</span></p>
                <p>高傲<span>{myPlayer?.pride}</span></p>
                <p>野心<span>{myPlayer?.ambition}</span></p>
                <p>毅力<span>{myPlayer?.persistence}</span></p>
                <p>耐心<span>{myPlayer?.patient}</span></p>
            </div>
        </div>

        <div class="flex justify-end pt-2">
            <button onclick={openModal} class="w-20 h-8 rounded-md cursor-pointer text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium text-sm text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
                编辑
            </button>
        </div>
    </VStack>

    <VStack className="w-1/4 mx-1">
        <RadarChart abilities={stats} />
        <StatusBars values={bars} />
        <PositionGrid />
    </VStack>

    <VStack className="grow h-full overflow-auto ml-1 pl-1">
        {#each abilityPairs as { label, value }}
            {@const tooltipText = `当前: ${value?.current ?? 'N/A'}<br>潜力: ${value?.currentMax ?? 'N/A'}<br>上限: ${value?.max ?? 'N/A'}`}
            <HStack className="items-center">
                <span class="w-24 text-sm">{label}</span>
                <Tooltip text={tooltipText} className="w-full">
                    <div class="flex w-full h-3 bg-gray-200 overflow-hidden dark:bg-neutral-700">
                        <div class="flex flex-col justify-center overflow-hidden bg-green-200 text-xs text-white text-center whitespace-nowrap" style="width: {toPercentString(value?.currentPercent)}"></div>
                        <div class="flex flex-col justify-center overflow-hidden bg-amber-400 text-xs text-white text-center whitespace-nowrap" style="width: {toPercentString(value?.currentMaxPercent)}"></div>
                        <div class="flex flex-col justify-center overflow-hidden bg-sky-300 text-xs text-white text-center whitespace-nowrap" style="width: {toPercentString(value?.maxPercent)}"></div>
                    </div>
                </Tooltip>
            </HStack>
        {/each}
    </VStack>
</HStack>

<Modal open={isModalOpen} close={closeModal}>
    <PlayersEditor player={myPlayer} onSave={onSaveSuccess} />
</Modal>

<style lang="postcss">
    @reference "tailwindcss";
    .sidebar {
        @apply w-full text-gray-900 bg-white border border-gray-200 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white overflow-y-auto text-xs;
    }
    .sidebar button {
        @apply relative cursor-pointer inline-flex items-center w-full px-4 py-1 text-sm font-medium border-b border-gray-200 rounded-t-lg hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700 dark:border-gray-600 dark:hover:bg-gray-600 dark:hover:text-white dark:focus:ring-gray-500 dark:focus:text-white;
    }
    .activate {
        @apply bg-gray-100 text-blue-700 dark:bg-gray-600 dark:text-white;
    }
    .badges {
        @apply cursor-pointer bg-blue-100 text-blue-800 text-xs font-medium me-2 px-2.5 py-0.5 rounded-sm dark:bg-blue-900 dark:text-blue-300;
    }
    p span {
        @apply pl-8 text-sm;
    }
</style>
