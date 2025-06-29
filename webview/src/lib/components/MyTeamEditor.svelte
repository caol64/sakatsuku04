<script lang="ts">
    import type { MyPlayer } from "$lib/models";
    import { onMount } from "svelte";
    import HStack from "./Stack/HStack.svelte";
    import RadarChart from "./RadarChart.svelte";
    import StatusBars from "./StatusBars.svelte";
    import PositionGrid from "./PositionGrid.svelte";
    import VStack from "./Stack/VStack.svelte";

    let myPlayers: MyPlayer[] = $state([]);
    let selectedPlayer = $state("");
    let stats = [0.9, 0.7, 0.6, 0.5, 0.8, 0.4];
    let bars = [0.9, 0.5, 0.7];

    async function fetchMyPlayer(name: string) {
        if (selectedPlayer !== name) {

        }
    }

    onMount(async () => {
        if (window.pywebview?.api?.fetch_my_team) {
            myPlayers = await window.pywebview.api.fetch_my_team();
            if (myPlayers) {
                selectedPlayer = myPlayers[0].name;
            }
        } else {
            alert('pywebview API 未加载');
        }
	});
</script>

<!-- <div class="flex w-full h-1.5 bg-gray-200 rounded-full overflow-hidden dark:bg-neutral-700">
  <div class="flex flex-col justify-center overflow-hidden bg-blue-400 text-xs text-white text-center whitespace-nowrap" style="width: 25%" role="progressbar" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100"></div>
  <div class="flex flex-col justify-center overflow-hidden bg-blue-700 text-xs text-white text-center whitespace-nowrap" style="width: 15%" role="progressbar" aria-valuenow="15" aria-valuemin="0" aria-valuemax="100"></div>
  <div class="flex flex-col justify-center overflow-hidden bg-gray-800 text-xs text-white text-center whitespace-nowrap dark:bg-white" style="width: 30%" role="progressbar" aria-valuenow="30" aria-valuemin="0" aria-valuemax="100"></div>
  <div class="flex flex-col justify-center overflow-hidden bg-orange-600 text-xs text-white text-center whitespace-nowrap" style="width: 5%" role="progressbar" aria-valuenow="5" aria-valuemin="0" aria-valuemax="100"></div>
</div> -->

<HStack className="flex-1 overflow-hidden py-2">
    <div class="w-1/4 overflow-y-auto text-xs">
        {#each myPlayers as item}
            <button onclick={() => fetchMyPlayer(item.name)} class={ selectedPlayer === item.name ? "activate" : "" }>
                { item.name }
            </button>
        {/each}
    </div>
    <VStack>
        <RadarChart abilities={stats} />
        <StatusBars values={bars} />
        <PositionGrid />
    </VStack>
</HStack>

<style lang="postcss">
    @reference "tailwindcss";
    div {
        @apply w-52 text-gray-900 bg-white border border-gray-200 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white;
    }
    button {
        @apply relative inline-flex items-center w-full px-4 py-1 text-sm font-medium border-b border-gray-200 rounded-t-lg hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700 dark:border-gray-600 dark:hover:bg-gray-600 dark:hover:text-white dark:focus:ring-gray-500 dark:focus:text-white;
    }
    .activate {
        @apply bg-gray-100 text-blue-700 dark:bg-gray-600 dark:text-white;
    }
</style>
