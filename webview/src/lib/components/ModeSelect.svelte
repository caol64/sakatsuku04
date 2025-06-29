<script lang="ts">
    import Ps2 from "$lib/icons/Ps2.svelte";
    import VStack from "$lib/components/Stack/VStack.svelte";
    import SaveFileSelect from "./SaveFileSelect.svelte";
</script>

<VStack className="flex flex-col items-center justify-center h-full w-full">
    <div class="flex justify-between space-x-8 w-11/12">
        <div class="flex-1 border border-dashed border-gray-300 rounded-md p-28 flex items-center justify-between bg-white">
            <SaveFileSelect />
        </div>

        <div class="flex-1 border border-dashed border-gray-300 rounded-md p-28 flex items-center justify-between bg-white">
            <div class="flex flex-col items-center justify-center space-y-1 w-full">
                <div class="text-gray-300 text-6xl">
                    <Ps2 />
                </div>
                <div class="flex flex-col space-y-2">
                    <div class="flex items-center space-x-2 text-sm">
                        <button class="text-blue-600 cursor-pointer flex items-center">
                            连接 PCSX2 模拟器
                            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</VStack>


<style lang="postcss">
    @reference "tailwindcss";
</style>
