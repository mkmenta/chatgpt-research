// function
function showNewMessage() {
    const newMessage = document.getElementById("newMessage");
    const newMessageInput = document.getElementById("newMessageInput");
    const newMessageInputHidden = document.getElementById("newMessageInputHidden");
    const sendButton = document.getElementById("sendButton");


    newMessage.textContent = newMessageInput.value;
    newMessageInputHidden.value = newMessageInput.value;
    // iterate over class new-messages
    const newMessages = document.getElementsByClassName("new-messages");
    for (let i = 0; i < newMessages.length; i++) {
        newMessages[i].style.display = '';
    }
    sendButton.disabled = true;
    newMessageInput.value = '';
    newMessageInput.disabled = true;
    allMessages.scrollTo(0, allMessages.scrollHeight);
    return true;
}

function setSpinningIfWriting() {
    const allMessages = document.getElementsByClassName("messages")
    const lastMessage = allMessages[allMessages.length - 1]
    if (lastMessage.getElementsByTagName("span")[0].textContent == "Writing...") {
        lastMessage.getElementsByTagName("span")[0].innerHTML = '<i>Writing...</i>'
        lastMessage.getElementsByTagName("img")[0].classList.add("round-and-round")

        const sendButton = document.getElementById("sendButton");
        const newMessageInput = document.getElementById("newMessageInput");
        newMessageInput.disabled = true;
        sendButton.disabled = true;

        window.setTimeout(function () {
            location.reload();
        }, 3000);
    }
}
setSpinningIfWriting()