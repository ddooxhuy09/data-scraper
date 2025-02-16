function randomMouseMove() {
    let x = Math.random() * window.innerWidth;
    let y = Math.random() * window.innerHeight;
    let event = new MouseEvent("mousemove", {
        bubbles: true,
        cancelable: true,
        clientX: x,
        clientY: y
    });
    document.dispatchEvent(event);
}

function randomScrollAndClick() {
    let seeMoreButton = document.querySelector('div._3HKY2899 div[role="button"]');
    
    let scrollUp = Math.floor(Math.random() * 50) + 20; // Cuộn lên từ 20px - 70px
    window.scrollBy({ top: -scrollUp, behavior: "smooth" });

    if (seeMoreButton) {
        let scrollDistance = Math.floor(Math.random() * 300) + 100; // Cuộn ngẫu nhiên từ 100px đến 400px
        window.scrollBy({ top: scrollDistance, behavior: "smooth" });

        setTimeout(() => {
            seeMoreButton.scrollIntoView({ behavior: "smooth", block: "center" });

            setTimeout(() => {
                // Mô phỏng hover chuột trước khi click
                let hoverEvent = new MouseEvent("mouseover", { bubbles: true, cancelable: true, view: window });
                seeMoreButton.dispatchEvent(hoverEvent);

                setTimeout(() => {
                    // Dùng PointerEvent để mô phỏng click thật hơn
                    let clickEvent = new PointerEvent("click", { bubbles: true, cancelable: true });
                    seeMoreButton.dispatchEvent(clickEvent);

                    console.log("Đã click vào nút See more.");

                    setTimeout(randomScrollAndClick, Math.random() * 5000 + 2000); // Thời gian giữa các lần click từ 2s - 7s
                }, Math.random() * 1000 + 500); // Hover 0.5s - 1.5s trước khi click
            }, Math.random() * 1000 + 500); // Chờ sau khi scroll
        }, Math.random() * 1000 + 500); // Chờ sau khi cuộn
    } else {
        console.log("Không còn nút để click.");
    }
}

// Chạy chuột ngẫu nhiên để mô phỏng hành vi người dùng
setInterval(randomMouseMove, Math.random() * 3000 + 2000); // Di chuyển chuột mỗi 2-5 giây

randomScrollAndClick();
