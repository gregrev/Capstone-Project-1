const BASE_URL = "https://gittrend.onrender.com";

// REMOVE/DELETE FAVORITE FROM USER'S PAGE

$("#repo-table").on("click", ".delete-button", async function (evt) {
    evt.preventDefault();
    let $row = $(evt.target).closest("tr");
    let repoId = $row.data("repo-id");

    try {
        await axios.post(`${BASE_URL}/repos/${repoId}/favorite`);
        $row.remove();
    } catch (error) {
        console.error(error);
    }
});

$("#dev-table").on("click", ".delete-button", async function (evt) {
    evt.preventDefault();
    let $row = $(evt.target).closest("tr");
    let devId = $row.data("dev-id");

    try {
        await axios.post(`${BASE_URL}/devs/${devId}/favorite`);
        $row.remove();
    } catch (error) {
        console.error(error);
    }
});

// ADD FAVORITE FROM TRENDING REPO/DEV PAGE

$("#repo-cards").on("submit", ".repo-form", async function (evt) {
    evt.preventDefault(); 
  
    let $form = $(evt.target);
    let $button = $form.find("button");
    let repoId = $form.data("repo-id");
  
    try {
      await axios.post(`${BASE_URL}/repos/${repoId}/favorite`);
  
      // toggle star
      $button.toggleClass("star-active");
      $button.find("i").toggleClass("star-active");
    } catch (error) {
      console.error(error);
    }
  });


$("#dev-cards").on("submit", ".dev-form", async function(evt) {
  evt.preventDefault(); 
  let $form = $(evt.target); 
  let $button = $form.find("button");
  let devId = $form.data("dev-id");

  try {
    await axios.post(`${BASE_URL}/devs/${devId}/favorite`);

    // toggle dstar
    $button.toggleClass("star-active");
    $button.find("i").toggleClass("star-active");
  } catch (error) {
    console.error(error);
  }
});

// HANDLE DROP DOWN MENU



// $("#dev-cards").on("submit", ".likebtn", async function (evt) {
//     evt.preventDefault();
//     let $card = $(evt.target).closest("ul");
//     let devId = $card.attr("data-dev-id");
//     console.log(devId);

//     await axios.post(`${BASE_URL}/devs/${devId}/favorite`);
    
// });


