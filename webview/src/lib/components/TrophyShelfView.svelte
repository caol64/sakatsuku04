<script lang="ts">
    import type { Trophy } from "$lib/models";
    import { onMount } from "svelte";
    import HStack from "./Stack/HStack.svelte";
    import { getRefreshFlag, getSelectedTab, setRefreshFlag } from "$lib/globalState.svelte";
    import { getTrophyData } from "$lib/utils";

    const rows: number[] = [7, 7, 8, 7];
    const trophyIndex = [51, 52, 48, 41, 14, 12, 39, 40, 15, 3, 17, 6, 50, 49, 13, 33, 4, 2, 0, 1, 16, 37, 47, 5, 10, 32, 36, 11, 9];
    let trophies: Trophy[] = $state([]);
    let myTrophies: Trophy[] = $derived.by(() => {
        return trophyIndex
            .map((id) => {
                const t = trophies[id];
                if (!t) return null;
                return {
                    ...t,
                    index: id
                };
            })
            .filter(Boolean) as Trophy[];
    });

    async function fetch() {
        if (window.pywebview?.api?.fetch_my_trophies) {
            trophies = await window.pywebview.api.fetch_my_trophies();
        } else {
            alert('API 未加载');
        }
    }

    // helper to get slice for each row
    function rowSlice(rowIndex: number) {
        const start = rows.slice(0, rowIndex).reduce((a, b) => a + b, 0);
        const len = rows[rowIndex];
        return myTrophies.slice(start, start + len);
    }

    onMount(async () => {
        fetch();
	});

    $effect(() => {
        if(getRefreshFlag() && getSelectedTab() === "Trophy") {
            try {
                fetch();
            } finally {
                setRefreshFlag(false);
            }
        }
    });
</script>

<div class="p-6 w-full mx-auto overflow-y-hidden">
    <div class="text-center mb-6">
        <h2 class="text-2xl font-bold">奖杯陈列</h2>
    </div>

    <div class="space-y-6">
        {#each rows as _, rowIndex}
            <!-- Each row: we center the row and allow cards to stretch equally -->
            <div class="w-full flex justify-center">
                <div
                    class="grid gap-4"
                    style="grid-template-columns: repeat({rows[
                        rowIndex
                    ]}, minmax(0, 1fr)); width: 100%;"
                >
                    {#each rowSlice(rowIndex) as trophy, _}
                        <div
                            class="relative flex flex-col justify-between rounded-lg border border-slate-200 p-4 shadow-sm hover:shadow-lg transition-shadow duration-200 overflow-hidden"
                        >
                            <!-- visual placeholder for trophy icon -->
                            <div class="flex items-center gap-3">
                                <p
                                    class="text-sm font-medium text-center w-full"
                                >
                                    {trophy.index !== undefined && getTrophyData()[trophy.index]}
                                </p>
                            </div>

                            <div class="mt-4 items-center justify-between">
                                <HStack
                                    className="items-center gap-2 justify-center"
                                >
                                    <div class="text-lg font-semibold">
                                        {trophy.winTimes}
                                    </div>
                                    <div class="text-xs text-slate-400">次</div>
                                </HStack>
                            </div>
                        </div>
                    {/each}
                </div>
            </div>
        {/each}
    </div>
</div>
