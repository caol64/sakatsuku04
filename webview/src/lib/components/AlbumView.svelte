<script lang="ts">
    import albumJson from "$locales/album_zh.json";
    import { onMount } from "svelte";
    import Tooltip from "./Tooltip.svelte";
    import Comment from "$lib/icons/Comment.svelte";
    import { getRefreshFlag, getSelectedTab, setRefreshFlag } from "$lib/globalState.svelte";

    type Player = {
        name: string;
        pos: string;
        index: number;
        collected?: boolean;
    };

    type PlayerGroup = {
        group: string;
        desc?: string;
        players: Player[];
    };

    let rawData: number[] = $state([]);

    const jsonData: PlayerGroup[] = albumJson;
    let enrichedData: PlayerGroup[] = $derived.by(() => {
        const data = jsonData.map(group => ({
            ...group,
            players: group.players.map(player => {
                const newPlayer = {
                    ...player,
                    collected: rawData.includes(player.index)
                };
                return newPlayer;
            })
        }));
        return data;
    });

    // 收集统计
    let totalPlayers = $derived(enrichedData.flatMap((g) => g.players).length);
    let collectedCount = $derived(
        enrichedData
            .flatMap((g) => g.players)
            .filter((p) => p.collected).length
        );
    let percentage = $derived(((collectedCount / totalPlayers) * 100).toFixed(1));

    async function fetch() {
        if (window.pywebview?.api?.fetch_my_album_players) {
            rawData = await window.pywebview.api.fetch_my_album_players();
        } else {
            alert('API 未加载');
        }
    }

    onMount(async () => {
        fetch();
	});

    $effect(() => {
        if(getRefreshFlag() && getSelectedTab() === "Album") {
            try {
                fetch();
            } finally {
                setRefreshFlag(false);
            }
        }
    });
</script>

<div class="p-6 w-full mx-auto overflow-y-auto">
    <!-- 顶部统计 -->
    <div class="text-center mb-6">
        <h2 class="text-2xl font-bold">
            名鉴球员收集进度
        </h2>
        <p class="text-sm text-gray-500 dark:text-gray-300 mt-1">
            已收集 {collectedCount} / {totalPlayers} ({percentage}%)
        </p>
        <div class="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full mt-3">
            <div
                class="h-full bg-green-500 rounded-full"
                style="width: {percentage}%"
            ></div>
        </div>
    </div>

    <!-- 分组显示 -->
    {#each enrichedData as group}
        <div class="mb-6">
            <h3 class="text-lg font-semibold text-gray-700 dark:text-white mb-2">
                {group.group}
                {#if group.desc}
                    {@const tooltipText = `${group.desc}`}
                    <Tooltip text={tooltipText} width="400px">
                        <Comment />
                    </Tooltip>
                {/if}
            </h3>
            <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
                {#each group.players as player}
                    <div class="p-2 border rounded shadow-sm transition-all
                        {player.collected
                            ? 'bg-white dark:bg-gray-800 border-green-500'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-400 border-gray-300'}"
                    >
                        <p class="font-semibold text-sm">{player.name}</p>
                        <p class="text-xs">{player.pos}</p>
                    </div>
                {/each}
            </div>
        </div>
    {/each}
</div>
