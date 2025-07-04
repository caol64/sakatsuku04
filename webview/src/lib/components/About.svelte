<script lang="ts">
    import Info from "$lib/icons/Info.svelte";
    import { onMount } from "svelte";
    import GithubButton from "./GithubButton.svelte";
    import Modal from "./Modal.svelte";

    let isModalOpen = $state(false);
    let version = $state("");

    function openModal() {
        isModalOpen = true;
    }

    function closeModal() {
        isModalOpen = false;
    }

    onMount(async () => {
        if (window.pywebview?.api?.get_version) {
            version = await window.pywebview.api.get_version();
        } else {
            alert('API 未加载');
        }
    });
</script>

<button class="cursor-pointer mx-2" onclick={openModal}>
    <Info />
    <span class="sr-only">More</span>
</button>

<Modal open={isModalOpen} close={closeModal} maxWidth="max-w-md">
    <!-- Modal header -->
    <div
        class="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-600 rounded-t bg-gray-50 dark:bg-gray-800"
    >
        <h3 class="text-2xl font-bold text-gray-900 dark:text-white tracking-wide">
            球会04修改器
        </h3>
    </div>

    <!-- Modal body -->
    <div class="px-6 py-6 space-y-6 bg-white dark:bg-gray-900 rounded-b">
        <div class="text-center space-y-2 text-gray-700 dark:text-gray-300">
            <p class="text-base">
                <span class="font-semibold">作者：</span> <a href="https://babyno.top/" class="text-blue-600 dark:text-blue-500 hover:underline" target="_blank">路边的阿不</a>
            </p>
            <p class="text-base">
                <span class="font-semibold">版本：</span> {version}
            </p>
        </div>

        <div class="flex flex-wrap gap-4 items-center justify-center">
            <a href="https://yuzhi.tech/contact" target="_blank"
                class="inline-flex items-center justify-center px-4 py-2 rounded-md text-white bg-blue-600 hover:bg-blue-700 transition"
            >
                问题反馈
            </a>
            <a
                href="https://yuzhi.tech/sponsor"
                target="_blank"
                class="inline-flex items-center justify-center px-4 py-2 rounded-md text-white bg-green-600 hover:bg-green-700 transition"
            >
                赞助
            </a>
            <GithubButton href="https://github.com/caol64/sakatsuku04" />
        </div>

        <p class="text-center text-sm text-gray-400 dark:text-gray-500 mt-8">
            © 2025 Lei Cao. All rights reserved.
        </p>
    </div>
</Modal>
