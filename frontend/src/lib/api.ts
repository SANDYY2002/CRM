const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

export type Organization = { id:number; name:string; slug:string; logo_url:string; timezone:string };
export type User = { id:number; username:string; email:string; first_name:string; last_name:string; phone:string; avatar_url:string; role:string; is_online:boolean };
export type Customer = { id:number; organization:number; first_name:string; last_name?:string; full_name?:string; email?:string; phone?:string; company?:string; avatar_url?:string; notes?:string; tags?:{id:number;name:string;color?:string}[] };
export type Lead = { id:number; organization:number; customer:number; customer_name:string; title:string; status:string; source?:string; value?:string|number; assigned_to:number|null; assigned_to_name:string|null; description:string };
export type Conversation = { id:number; organization:number; customer:number; customer_name:string; channel:number; channel_name:string; channel_type:string; assigned_to:number|null; assigned_to_name:string|null; status:string; unread_count:number; last_message_at:string|null };
export type Message = { id:number; conversation:number; sender:number|null; sender_name:string; direction:'inbound'|'outbound'|'internal'; message_type:string; content:string; attachment_url:string; metadata:Record<string,unknown>; is_read:boolean; created_at:string };
export type DashboardResponse = { organization_id:number; stats:{conversations:number;customers:number;leads:number;unread_messages:number}; recent_activity:{id:number;customer:string;channel:string;content:string;direction:string;created_at:string}[] };
export type Channel = { id:number; organization:number; type:string; name:string; external_id:string; is_active:boolean; metadata:Record<string, unknown> };
export type ChannelHealth = { id:number; type:string; connected:boolean; missing:string[]; external_id:string };
export type YouTubeVideo = { id:string; snippet?:{title?:string;description?:string;publishedAt?:string;thumbnails?:Record<string,{url?:string}>}; status?:{privacyStatus?:string}; statistics?:Record<string,string> };

async function request<T>(path:string, options:RequestInit={}):Promise<T>{
  const token=localStorage.getItem('crm_access_token');
  const organizationId=localStorage.getItem('crm_organization_id');
  const headers:Record<string,string>={};

  if(!(options.body instanceof FormData)) headers['Content-Type']='application/json';
  if(token) headers.Authorization=`Bearer ${token}`;
  if(organizationId) headers['X-Organization-ID']=organizationId;

  if(options.headers){
    const incoming=new Headers(options.headers);
    incoming.forEach((value,key)=>{headers[key]=value;});
  }

  const response=await fetch(`${API_URL}${path}`,{...options,headers});
  const data=await response.json().catch(()=>({}));
  if(!response.ok)throw new Error(data.detail||'Request failed');
  return data as T;
}

export const api={
  login:(payload:{username:string;password:string})=>request<{user:User;organizations:Organization[];access:string;refresh:string}>('/auth/login/',{method:'POST',body:JSON.stringify(payload)}),
  register:(payload:{username:string;password:string;email?:string;first_name?:string;last_name?:string;organization_name:string})=>request<{user:User;organization:Organization;access:string;refresh:string}>('/auth/register/',{method:'POST',body:JSON.stringify(payload)}),
  me:()=>request<{user:User;organizations:Organization[]}>('/auth/me/'),
  dashboard:()=>request<DashboardResponse>('/dashboard/'),
  customers:()=>request<Customer[]>('/customers/'),
  customer:(id:number)=>request<Customer>(`/customers/${id}/`),
  leads:()=>request<Lead[]>('/leads/'),
  conversations:()=>request<Conversation[]>('/conversations/'),
  conversationMessages:(conversationId:number)=>request<Message[]>(`/messages/?conversation=${conversationId}`),
  sendMessage:(conversationId:number,content:string)=>request<Message>('/messages/',{method:'POST',body:JSON.stringify({conversation:conversationId,content,message_type:'text'})}),
  markConversationRead:(id:number)=>request<Conversation>(`/conversations/${id}/mark_read/`,{method:'POST'}),
  channels:()=>request<Channel[]>('/channels/'),
  channelHealth:(id:number)=>request<ChannelHealth>(`/channels/${id}/health/`,{method:'POST'}),
  youtubeOAuthUrl:()=>request<{authorization_url:string}>('/youtube/oauth/url/'),
  uploadYouTubeVideo:({channelId,video,title,description,tags,privacy}:{channelId:number;video:File;title:string;description:string;tags:string;privacy:string})=>{const form=new FormData();form.append('channel_id',String(channelId));form.append('video',video);form.append('title',title);form.append('description',description);form.append('tags',tags);form.append('privacy_status',privacy);return request<{id:string;title:string}>('/youtube/upload/',{method:'POST',body:form});},
  youtubeVideos:(channelId:number)=>request<{items:YouTubeVideo[];nextPageToken?:string}>(`/youtube/channels/${channelId}/videos/`).then((data)=>data.items),
  youtubeVideo:(channelId:number,videoId:string)=>request<YouTubeVideo>(`/youtube/channels/${channelId}/videos/${encodeURIComponent(videoId)}/`),
  updateYouTubeVideo:(channelId:number,videoId:string,payload:Record<string,unknown>)=>request<YouTubeVideo>(`/youtube/channels/${channelId}/videos/${encodeURIComponent(videoId)}/`,{method:'PATCH',body:JSON.stringify(payload)}),
  deleteYouTubeVideo:(channelId:number,videoId:string)=>request<void>(`/youtube/channels/${channelId}/videos/${encodeURIComponent(videoId)}/`,{method:'DELETE'}),
  youtubeComments:(channelId:number,videoId:string)=>request<{items:unknown[]}>(`/youtube/channels/${channelId}/videos/${encodeURIComponent(videoId)}/comments/`),
  replyToYouTubeComment:(channelId:number,commentId:string,text:string)=>request<unknown>(`/youtube/channels/${channelId}/comments/${encodeURIComponent(commentId)}/reply/`,{method:'POST',body:JSON.stringify({text})}),
};
