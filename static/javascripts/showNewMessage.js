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
    return true;
}