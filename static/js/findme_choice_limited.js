    document.addEventListener('DOMContentLoaded', function () {
  
      function applyCheckboxLimit(groupClassName, maxCount) {
        const checkboxes = document.querySelectorAll(`.${groupClassName}-checkbox`);
        const errorMessage = document.getElementById(`${groupClassName}-error`);
  
        checkboxes.forEach(function (checkbox) {
          checkbox.addEventListener('change', function () {
            const checkedBoxes = document.querySelectorAll(`.${groupClassName}-checkbox:checked`);
            if (checkedBoxes.length > maxCount) {
              checkbox.checked = false; // チェックを外す
              if (errorMessage) {
                errorMessage.style.display = 'block'; // エラーメッセージを表示
              }
            } else {
              if (errorMessage) {
                errorMessage.style.display = 'none'; // メッセージを非表示
              }
            }
          });
        });
      }
  
      // 以下に複数のチェック制限を適用
      applyCheckboxLimit('hobby_choice', 3);
      applyCheckboxLimit('food_choice', 3);
      applyCheckboxLimit('music_choice', 3);
      applyCheckboxLimit('movie_choice', 3);
      applyCheckboxLimit('book_choice', 3);
      applyCheckboxLimit('personality_type_choice', 3);
      applyCheckboxLimit('favorite_date_choice', 3);
      applyCheckboxLimit('sense_of_values_choice', 3);
      applyCheckboxLimit('future_plan_choice', 3);
      applyCheckboxLimit('request_for_partner_choice', 3);
      applyCheckboxLimit('weekend_activity_choice', 3);
      applyCheckboxLimit('on_going_project_choice', 3);
      applyCheckboxLimit('social_activity_choice', 3);
      applyCheckboxLimit('free_day_choice', 3);
      applyCheckboxLimit('proudest_achievements_choice', 3);
      applyCheckboxLimit('most_important_values_choice', 3);
    });