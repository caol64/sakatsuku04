<script lang="ts">
    import type { BPlayer } from "$lib/models";
    import { onMount } from "svelte";
    import HStack from "./Stack/HStack.svelte";
    import RadarChart from "./RadarChart.svelte";
    import StatusBars from "./StatusBars.svelte";
    import VStack from "./Stack/VStack.svelte";
    import Tooltip from "./Tooltip.svelte";
    import { getCooperationType, getGrowType, getPosition, getRank, getRegion, getStyle, getToneType, getFoot, sortedAbilities } from "$lib/utils";
    import AbilityBar from "./AbilityBar.svelte";
    import abilEval from "$locales/abil_eval_zh.json";
    import Comment from "$lib/icons/Comment.svelte";
    import Skull from "$lib/icons/Skull.svelte";
    import Waveform from "./Waveform.svelte";
    import PositionGrid from "./PositionGrid.svelte";

    let { selectedPlayer = 0, selectedYear = 0 } = $props();

    let bPlayer: BPlayer = $state({hexagon: [], odc: [], abilities: []});
    let stats = $state(Array(6).fill(0));
    let bars = $state([0, 0, 0]);

    let abilityPairs = $derived(
        sortedAbilities.map((label, i) => ({
            label,
            value: [0, 0, bPlayer.abilities[i]]
        }))
    );

    async function fetchBPlayer() {
        if (window.pywebview?.api?.get_bplayer) {
            bPlayer = await window.pywebview.api.get_bplayer(selectedPlayer, selectedYear);
            stats = bPlayer.hexagon;
            bars = [bPlayer.odc[0], bPlayer.odc[1], 0];
        } else {
            alert('API 未加载');
        }
    }

    onMount(async () => {
        fetchBPlayer();
	});

    $effect(() => {
        if(selectedPlayer || selectedYear) {
            fetchBPlayer();
        }
    });

</script>

<VStack className="w-1/5 mx-1">
    <div class="border border-gray-200 dark:border-gray-600 rounded-md p-4 space-y-2 bg-gray-50 dark:bg-gray-700">
        <p class="flex items-center justify-between select-text">
            姓名
            <span class="flex-1 pl-8 text-sm">{bPlayer?.name}</span>
            {#if bPlayer?.spComment}
                {@const tooltipText = `${bPlayer.spComment}`}
                <Tooltip text={tooltipText} width="250px">
                    <Comment />
                </Tooltip>
            {/if}
        </p>
        <p>
            位置
            <span class="pl-8 text-sm">{getPosition(bPlayer?.pos)}</span>
        </p>
        <p>
            基础年龄
            <span class="pl-8 text-sm">{bPlayer?.age}</span>
        </p>
        <p>
            出生地
            <span class="pl-8 text-sm">{getRegion(bPlayer?.born)}</span>
        </p>
        <p>
            惯用脚
            <span class="pl-8 text-sm">{getFoot(bPlayer?.foot)}</span>
        </p>
        <p>
            身高
            <span class="pl-8 text-sm">{bPlayer?.height}</span>
        </p>
        <p>
            风格
            <span class="pl-8 text-sm">{getStyle(bPlayer?.style)}</span>
        </p>
        <p>
            对战评价
            <span class="pl-8 text-sm">{getRank(bPlayer?.rank)}</span>
        </p>
        <p>
            出现年份
            <span class="pl-8 text-sm">{bPlayer?.debutYear}</span>
        </p>
        <p>
            签约所需声望
            <span class="pl-8 text-sm">{bPlayer?.signingDifficulty}</span>
        </p>
        <p class="flex items-center justify-between">
            连携
            <span  class="flex-1 pl-8 text-sm">{getCooperationType(bPlayer?.cooperationType)}</span>
            {#if bPlayer?.baddenPlayers}
                {@const tooltipText = `连携崩坏：<br>${bPlayer.baddenPlayers.join("<br>")}`}
                <Tooltip text={tooltipText} width="100px">
                    <Skull />
                </Tooltip>
            {/if}
        </p>
        <p>
            性格
            <span class="pl-8 text-sm">{getToneType(bPlayer?.toneType)}</span>
        </p>
        <p>成长类型</p>
        <div class="pl-4 grid grid-cols-3 gap-x-2 text-sm text-left">
            <div>身体</div>
            <div>技术</div>
            <div>头脑</div>
            <div>{getGrowType(bPlayer?.growTypePhy)}</div>
            <div>{getGrowType(bPlayer?.growTypeTec)}</div>
            <div>{getGrowType(bPlayer?.growTypeSys)}</div>
        </div>
        <p>隐藏属性</p>
        <div class="pl-4 grid grid-cols-2 gap-x-1 text-sm text-left">
            <div><span>人气</span><span class="pl-3">{bPlayer?.pop}</span></div>
            <div><span>欲望</span><span class="pl-3">{bPlayer?.desire}</span></div>
            <div><span>自尊</span><span class="pl-3">{bPlayer?.pride}</span></div>
            <div><span>野心</span><span class="pl-3">{bPlayer?.ambition}</span></div>
            <div><span>毅力</span><span class="pl-3">{bPlayer?.persistence}</span></div>
            <div><span>耐心</span><span class="pl-3">{bPlayer?.patient}</span></div>
            <div><span>超级替补</span><span class="pl-3">{bPlayer?.superSub}</span></div>
            <div><span>公平竞赛</span><span class="pl-3">{bPlayer?.wildType}</span></div>
            <div><span>受伤耐性</span><span class="pl-3">{bPlayer?.weakType}</span></div>
            <div><span>疲劳耐性</span><span class="pl-3">{bPlayer?.tiredType}</span></div>
            <div><span>波动指数</span><span class="pl-3">{bPlayer?.waveType}</span></div>
        </div>
    </div>
</VStack>
<VStack className="w-3/10 mx-1">
    {#if bPlayer?.abilEval}
        <Tooltip text={abilEval[bPlayer.abilEval]} width="220px">
            <RadarChart abilities={stats} />
        </Tooltip>
    {/if}
    <HStack className="w-full grid grid-cols-2">
        <StatusBars values={bars} pos={bPlayer.pos} />
        <PositionGrid aposEval={bPlayer.aposEval} />
    </HStack>
    <Waveform phyGrows={bPlayer?.phyGrows} tecGrows={bPlayer?.tecGrows} sysGrows={bPlayer?.sysGrows} />
    {#if bPlayer?.abilEval}
        <div class="border border-gray-200 dark:border-gray-600 rounded-md py-2 px-3 space-y-2 bg-gray-50 dark:bg-gray-700 my-2">
            <p>{abilEval[bPlayer.abilEval]}</p>
        </div>
    {/if}
</VStack>

<VStack className="grow h-full overflow-auto ml-1 pl-1 pb-12">
    {#each abilityPairs as { label, value }}
        <HStack className="items-center">
            <span class="w-24 text-sm">{label}</span>
            {#if value}
                {@const tooltipText = `上限: ${value[2]}`}
                <Tooltip text={tooltipText} className="w-full">
                    <AbilityBar abilities={value} />
                </Tooltip>
            {/if}
        </HStack>
    {/each}
</VStack>
