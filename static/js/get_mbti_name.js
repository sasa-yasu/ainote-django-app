document.addEventListener("DOMContentLoaded", function() {
    var mbtiSelect = document.getElementById("id_mbti");
    var mbtiNameSelect = document.getElementById("id_mbti_name");

    function updateMbtiNameChoices(mbti, selectedValue) {
        if (mbti) {
            fetch(`/${appName}/get_mbti_name_choices/?mbti=${mbti}`)
                .then(response => response.json())
                .then(data => {
                    mbtiNameSelect.innerHTML = "<option value=''>Select MBTI Name</option>";
                    data.mbti_name_choices.forEach(choice => {
                        var option = document.createElement("option");
                        option.value = choice[0];
                        option.textContent = choice[1];
                        if (choice[0] === selectedValue) {
                            option.selected = true;
                        }
                        mbtiNameSelect.appendChild(option);
                    });
                });
        } else {
            mbtiNameSelect.innerHTML = "<option value=''>Select MBTI Type first</option>";
        }
    }

    // ページロード時に選択肢を更新
    updateMbtiNameChoices(mbtiSelect.value, mbtiNameSelect.dataset.selected);

    // `mbti` が変更されたときに `mbti_name` を更新
    mbtiSelect.addEventListener("change", function() {
        updateMbtiNameChoices(this.value, null);
    });
});