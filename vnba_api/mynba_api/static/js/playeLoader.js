let offset = 6;
const teamSlug = "{{ team_slug }}";
let isLoading = false; // 防止重複請求

async function loadNextBatch() {
    if (isLoading) return; // 如果正在載入，直接返回

    isLoading = true;
    console.log(`📡 正在載入更多球員... (offset: ${offset})`);

    try {
        const response = await fetch(`/${teamSlug}/roster}?offset=${offset}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest' // 確保後端識別為 AJAX 請求
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.players.length === 0) {
            console.log("⚠️ 沒有更多球員可載入！");
            return;
        }

        console.log(`✅ 成功載入 ${data.players.length} 位球員`);

        data.players.forEach(player => {
            const playerCard = document.createElement("div");
            playerCard.style = "border: 1px solid #ccc; padding: 10px; text-align: center; border-radius: 10px; margin-bottom: 10px;";

            playerCard.innerHTML = `
                <div style="font-size: 40px; font-weight: bold;">${player.jersey}</div>
                <img src="${player.headshot_url}" 
                     alt="${player.name} Headshot"
                     legacy="true"
                     loading="lazy"
                     width="1040" 
                     height="760" 
                     decoding="async"
                     data-nimg="1" 
                     style="color: transparent; width: 100%; height: auto;"
                     onerror="this.src='/static/default_player.png';">
                <div style="margin-top: 10px;">
                    <strong>${player.name || 'Unknown Player'}</strong>
                </div>
            `;

            document.getElementById("player-list").appendChild(playerCard);
        });

        offset += 6;

    } catch (error) {
        console.error("❌ 載入球員資料時發生錯誤:", error);
    } finally {
        isLoading = false;
    }
}

// 改善滾動事件監聽器
window.addEventListener("scroll", () => {
    // 計算是否接近頁面底部（提前 200px 觸發）
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const windowHeight = window.innerHeight;
    const documentHeight = Math.max(
        document.body.scrollHeight,
        document.body.offsetHeight,
        document.documentElement.clientHeight,
        document.documentElement.scrollHeight,
        document.documentElement.offsetHeight
    );

    if (scrollTop + windowHeight >= documentHeight - 200) {
        console.log("🔄 觸發載入更多球員");
        loadNextBatch();
    }
});

// 初始載入完成後的調試資訊
document.addEventListener('DOMContentLoaded', function() {
    console.log("📋 球員載入器已初始化");
    console.log(`🏀 當前球隊: ${teamSlug}`);
    console.log(`📊 初始 offset: ${offset}`);
});