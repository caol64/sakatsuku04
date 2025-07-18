<script lang="ts">
    import type { MyPlayer, MyTeamPlayer } from "$lib/models";
    import { onMount } from "svelte";
    import HStack from "./Stack/HStack.svelte";
    import RadarChart from "./RadarChart.svelte";
    import StatusBars from "./StatusBars.svelte";
    import VStack from "./Stack/VStack.svelte";
    import Tooltip from "./Tooltip.svelte";
    import Modal from "./Modal.svelte";
    import PlayersEditor from "./PlayersEditor.svelte";
    import { getCooperationType, getGrowType, getPlayerColor, getPosition, getRank, getRegion, getStyle, getToneType, preferFoot, sortedAbilities, getGrowEval } from "$lib/utils";
    import { getRefreshFlag, getSelectedTab, setRefreshFlag } from "$lib/globalState.svelte";
    import AbilityBar from "./AbilityBar.svelte";
    import Football from "$lib/icons/Football.svelte";
    import abilEval from "$locales/abil_eval_zh.json";
    import Comment from "$lib/icons/Comment.svelte";
    import Skull from "$lib/icons/Skull.svelte";
    import Waveform from "./Waveform.svelte";
    import PositionGrid from "./PositionGrid.svelte";

    let myPlayers: MyTeamPlayer[] = $state([]);
    let selectedPlayer = $state(0);
    let myPlayer: MyPlayer = $state({ abilities: [], hexagon: [], odc: [] });
    let stats = $state(Array(18).fill(0));
    let bars = $state([0, 0, 0]);
    let selectedTeam = $state(0);

    let abilityPairs = $derived(
        sortedAbilities.map((label, i) => ({
            label,
            value: myPlayer.abilities[i]
        }))
    );

    async function fetchMyPlayer(id: number) {
        if (window.pywebview?.api?.fetch_my_player) {
            myPlayer = await window.pywebview.api.fetch_my_player(id, selectedTeam);
            stats = myPlayer.hexagon;
            bars = [myPlayer.odc[0], myPlayer.odc[1], 0];
        } else {
            alert('API 未加载');
        }
    }

    async function fetchMyTeam() {
        if (window.pywebview?.api?.fetch_my_team) {
            myPlayers = await window.pywebview.api.fetch_my_team(selectedTeam);
            if (myPlayers && myPlayers.length > 0) {
                selectedPlayer = myPlayers[0].id;
                await fetchMyPlayer(selectedPlayer);
            } else {
                selectedPlayer = 0;
                myPlayer = { abilities: [], hexagon: [], odc: [] };
                stats = Array(18).fill(0);
                bars = [0, 0, 0];
            }
        } else {
            alert('API 未加载');
        }
    }

    $effect(() => {
        if(getRefreshFlag() && getSelectedTab() === "Players") {
            try {
                selectedTeam = 0;
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
        await fetchMyPlayer(selectedPlayer);
    }

    async function onPlayerClick(id: number) {
        if (selectedPlayer !== id) {
            selectedPlayer = id;
            await fetchMyPlayer(id);
        }
    }

    async function onTeamTabClick(index: number) {
        if (selectedTeam !== index) {
            selectedTeam = index;
            await fetchMyTeam();
        }
    }
</script>

<HStack className="flex-1 overflow-hidden m-2.5">
    <VStack className="w-1/5 mr-1">
        <HStack className="space-x-4 mb-2 mx-2">
            <button onclick={() => onTeamTabClick(0)} class="badges">一线队</button>
            <button onclick={() => onTeamTabClick(1)} class="badges">青年队</button>
        </HStack>
        {#if myPlayers && myPlayers.length > 0}
            <div class="sidebar">
                {#each myPlayers as item}
                    <button
                        onclick={() => onPlayerClick(item.id)}
                        class={selectedPlayer === item.id ? "activate" : ""}
                        style={`background-image: linear-gradient(to right, transparent 66%, ${getPlayerColor(item.pos)} 100%)`}
                    >
                        <span class="flex items-center justify-between w-full">
                            {item.name}
                            {#if item.isAlbum}
                                <div class="mx-2"><Football /></div>
                            {/if}
                        </span>
                    </button>
                {/each}
            </div>
        {:else}
            <div class="border text-sm border-gray-200 dark:border-gray-600 rounded-md p-4 space-y-2 bg-gray-50 dark:bg-gray-700">
                空空如也
            </div>
        {/if}
    </VStack>

    <VStack className="w-1/5 mx-1">
        <div class="border border-gray-200 dark:border-gray-600 rounded-md p-4 space-y-2 bg-gray-50 dark:bg-gray-700">
            <p class="flex items-center justify-between text-sm">
                姓名
                <span class="flex-1 pl-8">{myPlayer?.name}</span>
                {#if myPlayer?.spComment}
                    {@const tooltipText = `${myPlayer.spComment}`}
                    <Tooltip text={tooltipText} width="200px">
                        <Comment />
                    </Tooltip>
                {/if}
            </p>
            <p>
                位置
                <span class="pl-8 text-sm">{getPosition(myPlayer?.pos)}</span>
            </p>
            <p>
                年龄
                <span class="pl-8 text-sm">{myPlayer?.age}</span>
            </p>
            <p>
                号码
                <span class="pl-8 text-sm">{myPlayer?.number}</span>
            </p>
            <p>
                留学次数
                <span class="pl-8 text-sm">{myPlayer?.abroadTimes}</span>
            </p>
            <p>
                出生地
                <span class="pl-8 text-sm">{getRegion(myPlayer?.born)}</span>
            </p>
            <p>
                惯用脚
                <span class="pl-8 text-sm">{preferFoot(myPlayer?.foot)}</span>
            </p>
            <p>
                身高
                <span class="pl-8 text-sm">{myPlayer?.height}</span>
            </p>
            <p>
                风格
                <span class="pl-8 text-sm">{getStyle(myPlayer?.style)}</span>
            </p>
            <p>
                对战评价
                <span class="pl-8 text-sm">{getRank(myPlayer?.rank)}</span>
            </p>
            <p class="flex items-center justify-between text-sm">
                连携
                <span  class="flex-1 pl-8">{getCooperationType(myPlayer?.cooperationType)}</span>
                {#if myPlayer?.baddenPlayers}
                    {@const tooltipText = `连携崩坏：<br>${myPlayer.baddenPlayers.join("<br>")}`}
                    <Tooltip text={tooltipText} width="100px">
                        <Skull />
                    </Tooltip>
                {/if}
            </p>
            <p>
                性格
                <span class="pl-8 text-sm">{getToneType(myPlayer?.toneType)}</span>
            </p>
            <p>
                年薪
                {#if myPlayer?.salaryHigh}
                    <span class="pl-8 text-sm">
                        {myPlayer?.salaryHigh} 亿
                    </span>
                {/if}
                <span class="pl-{myPlayer?.salaryHigh ? '2' : '8'} text-sm">{myPlayer?.salaryLow} 万</span>
            </p>
            <p>
                合同
                <span class="pl-8 text-sm">{myPlayer?.offerYearsPassed} / {myPlayer?.offerYearsTotal}</span>
            </p>
            <p>成长类型</p>
            <div class="pl-4 grid grid-cols-3 gap-x-2 text-sm text-left">
                <div>身体</div>
                <div>技术</div>
                <div>头脑</div>
                <div>{getGrowType(myPlayer?.growTypePhy)}</div>
                <div>{getGrowType(myPlayer?.growTypeTec)}</div>
                <div>{getGrowType(myPlayer?.growTypeSys)}</div>
            </div>
            <!-- <p>修正指数<span>{myPlayer?.jlFactor}</span></p> -->
            <p>隐藏属性</p>
            <div class="pl-4  text-sm">
                <div><span>进取</span><span class="pl-8">{myPlayer?.desire}</span></div>
                <div><span>高傲</span><span class="pl-8">{myPlayer?.pride}</span></div>
                <div><span>野心</span><span class="pl-8">{myPlayer?.ambition}</span></div>
                <div><span>毅力</span><span class="pl-8">{myPlayer?.persistence}</span></div>
                <div><span>耐心</span><span class="pl-8">{myPlayer?.patient}</span></div>
            </div>
        </div>
        {#if selectedTeam === 0}
            <div class="flex justify-end pt-2">
                <button onclick={openModal} class="w-20 h-8 rounded-md cursor-pointer text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium text-sm text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
                    编辑
                </button>
            </div>
        {/if}
    </VStack>

    <VStack className="w-3/10 mx-1">
        {#if myPlayer?.maxAbilEval}
            <Tooltip text={abilEval[myPlayer.maxAbilEval]} width="200px">
                <RadarChart abilities={stats} />
            </Tooltip>
        {/if}
        <HStack className="w-full grid grid-cols-2">
            <StatusBars values={bars} pos={myPlayer.pos} />
            <PositionGrid aposEval={myPlayer.aposEval} />
        </HStack>
        <Waveform phyGrows={myPlayer?.phyGrows} tecGrows={myPlayer?.tecGrows} sysGrows={myPlayer?.sysGrows} currentAge={myPlayer?.age} />
        {#if myPlayer?.abilEval}
            <div class="border border-gray-200 dark:border-gray-600 rounded-md py-2 px-3 space-y-2 bg-gray-50 dark:bg-gray-700 my-2">
                <p>{abilEval[myPlayer.abilEval]}</p>
                <p>{getGrowEval(myPlayer.growEval)}</p>
            </div>
        {/if}
    </VStack>

    <VStack className="grow h-full overflow-auto ml-1 pl-1">
        {#each abilityPairs as { label, value }}
            <HStack className="items-center">
                <span class="w-24 text-sm">{label}</span>
                {#if value}
                    {@const tooltipText = `当前: ${value.current}<br>潜力: ${value.currentMax}<br>上限: ${value.max}`}
                    <Tooltip text={tooltipText} className="w-full">
                        <AbilityBar abilities={[value.current, value.currentMax, value.max]} />
                    </Tooltip>
                {/if}
            </HStack>
        {/each}
    </VStack>
</HStack>

<Modal open={isModalOpen} close={closeModal}>
    <PlayersEditor player={myPlayer} team={selectedTeam} onSave={onSaveSuccess} />
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
</style>
