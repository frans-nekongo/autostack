import { Component } from '@angular/core';
import { ChatSideBar } from "../../components/chat/chat-side-bar/chat-side-bar";
import { RouterModule } from "@angular/router";

@Component({
  selector: 'app-chat',
  imports: [ChatSideBar, RouterModule],
  templateUrl: './chat.html',
  styleUrl: './chat.scss'
})
export class Chat {

}
