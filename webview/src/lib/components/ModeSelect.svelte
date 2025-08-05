<script lang="ts">
    import VStack from "$lib/components/Stack/VStack.svelte";
    import SaveFileSelect from "./SaveFileSelect.svelte";
    import Pcsx2Connect from "./Pcsx2Connect.svelte";
    import { onMount } from "svelte";
    import About from "./About.svelte";
    import PlayerDB from "./PlayerDB.svelte";

    onMount(async () => {
        if (window.pywebview?.api?.reset) {
            await window.pywebview.api.reset();
        }
    });
</script>

<VStack className="flex flex-col items-center justify-center h-full w-full space-y-8">
    <div class="absolute top-4 right-2">
        <About />
    </div>
    <div class="flex justify-between space-x-8 w-11/12">
        <div class="flex-1 border border-dashed border-gray-300 rounded-md p-28 flex items-center justify-between">
            <SaveFileSelect />
        </div>

        <div class="flex-1 border border-dashed border-gray-300 rounded-md p-28 flex items-center justify-between">
            <Pcsx2Connect />
        </div>
    </div>
    <div class="w-11/12 border border-dashed border-gray-300 rounded-md p-12">
        <PlayerDB />
    </div>
</VStack>

