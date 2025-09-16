"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Plus, MessageSquare, Clock, Ticket, CheckCircle, AlertCircle, Phone, Mail, MessageCircle, Globe, Send, Camera, MessagesSquare } from "lucide-react"
import { useAuth } from "@/hooks/use-auth.ts"
import { apiFetch } from "@/lib/api"

// Channel utility functions
const getChannelIcon = (channel?: string) => {
  switch (channel) {
    case 'whatsapp':
      return <MessageCircle className="w-3 h-3" />
    case 'sms':
      return <Phone className="w-3 h-3" />
    case 'email':
      return <Mail className="w-3 h-3" />
    case 'telegram':
      return <Send className="w-3 h-3" />
    case 'instagram':
      return <Camera className="w-3 h-3" />
    case 'messenger':
      return <MessagesSquare className="w-3 h-3" />
    default:
      return <Globe className="w-3 h-3" />
  }
}

const getChannelColor = (channel?: string) => {
  switch (channel) {
    case 'whatsapp':
      return 'bg-green-100 text-green-800'
    case 'sms':
      return 'bg-blue-100 text-blue-800'
    case 'email':
      return 'bg-purple-100 text-purple-800'
    case 'telegram':
      return 'bg-cyan-100 text-cyan-800'
    case 'instagram':
      return 'bg-pink-100 text-pink-800'
    case 'messenger':
      return 'bg-blue-100 text-blue-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const getChannelName = (channel?: string) => {
  switch (channel) {
    case 'whatsapp':
      return 'WhatsApp'
    case 'sms':
      return 'SMS'
    case 'email':
      return 'Email'
    case 'telegram':
      return 'Telegram'
    case 'instagram':
      return 'Instagram'
    case 'messenger':
      return 'Messenger'
    default:
      return 'Web'
  }
}

type Conversation = {
  id: number
  user_id: number
  interaction: {
    question: string
    answer: string
    channel?: string
  }
  resolved: boolean
  created_at: string
  updated_at: string
}

type UserTicket = {
  id: number
  user_id: number
  topic: string
  status: string
  created_at: string
  updated_at: string
}

type ConversationSidebarProps = {
  currentConversationId?: string
  onConversationSelect: (conversationId: string) => void
  onNewConversation: () => void
  refreshKey?: number // Add refresh mechanism
}

export function ConversationSidebar({
  currentConversationId,
  onConversationSelect,
  onNewConversation,
  refreshKey = 0
}: ConversationSidebarProps) {
  const { token } = useAuth("user")
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [tickets, setTickets] = useState<UserTicket[]>([])
  const [loading, setLoading] = useState(false)

  // Fetch user's conversations
  useEffect(() => {
    const fetchConversations = async () => {
      if (!token) {
        console.log("No token available")
        return
      }
      
      try {
        setLoading(true)
        console.log("Fetching conversations...")
        const data = await apiFetch<Conversation[]>("/users/conversations", {}, token)
        console.log("Conversations data received:", data)
        console.log("Number of conversations:", data?.length || 0)
        setConversations(data)
      } catch (error) {
        console.error("Failed to fetch conversations:", error)
        setConversations([])
      } finally {
        setLoading(false)
      }
    }

    fetchConversations()
  }, [token, refreshKey])

  // Fetch user's tickets
  useEffect(() => {
    const fetchTickets = async () => {
      if (!token) return
      
      try {
        const data = await apiFetch<UserTicket[]>("/users/me/tickets", {}, token)
        setTickets(data)
      } catch (error) {
        console.error("Failed to fetch tickets:", error)
        setTickets([])
      }
    }

    fetchTickets()
  }, [token, refreshKey])

  const markTicketAsResolved = async (ticketId: number) => {
    if (!token) return

    if (confirm("Are you sure you want to mark this ticket as resolved?")) {
      try {
        await apiFetch(
          `/users/me/tickets/${ticketId}/resolve`,
          {
            method: "PATCH",
          },
          token
        )
        
        alert("Ticket marked as resolved!")
        
        // Update local state to reflect the change
        setTickets(prev => prev.map(ticket => 
          ticket.id === ticketId 
            ? { ...ticket, status: 'resolved' }
            : ticket
        ))
      } catch (error) {
        console.error("Failed to resolve ticket:", error)
        alert("Failed to mark ticket as resolved. Please try again.")
      }
    }
  }

  return (
    <div className="w-80 bg-gray-900 border-r border-gray-700 flex flex-col h-screen">
      <div className="p-4 border-b border-gray-700 flex-shrink-0">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">Chat History</h2>
          <Button size="sm" onClick={onNewConversation}>
            <Plus className="w-4 h-4 mr-1" />
            New
          </Button>
        </div>

        <Tabs defaultValue="conversations" className="w-full">
          <TabsList className="grid w-full grid-cols-2 bg-gray-800">
            <TabsTrigger value="conversations" className="text-sm text-gray-300 data-[state=active]:bg-gray-700 data-[state=active]:text-white">
              <MessageSquare className="w-4 h-4 mr-1" />
              Conversations
            </TabsTrigger>
            <TabsTrigger value="tickets" className="text-sm text-gray-300 data-[state=active]:bg-gray-700 data-[state=active]:text-white">
              <Ticket className="w-4 h-4 mr-1" />
              Tickets
            </TabsTrigger>
          </TabsList>

          <TabsContent value="conversations" className="mt-4">
            <ScrollArea className="h-[calc(100vh-200px)]">
              <div className="space-y-3">
                {loading ? (
                  <Card>
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-center">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                          <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                          <span className="ml-2 text-sm text-gray-400">Loading conversations...</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ) : conversations.length > 0 ? (
                  conversations.map((conversation: Conversation) => (
                    <div
                      key={conversation.id}
                      className={`cursor-pointer transition-all duration-200 rounded-lg border p-4 hover:shadow-md ${
                        conversation.resolved 
                          ? 'bg-green-900 border-green-700 hover:bg-green-800 hover:border-green-600' 
                          : currentConversationId === conversation.id.toString() 
                            ? 'bg-gray-700 border-gray-600 shadow-sm hover:border-gray-500' 
                            : 'bg-gray-800 border-gray-600 hover:bg-gray-700 hover:border-gray-500'
                      }`}
                      onClick={() => onConversationSelect(conversation.id.toString())}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${conversation.resolved ? 'bg-green-500' : 'bg-gray-500'}`} />
                          <span className="text-sm font-semibold text-gray-200">Conversation #{conversation.id}</span>
                          <Badge 
                            variant="outline" 
                            className={`text-xs px-1.5 py-0.5 ${getChannelColor(conversation.interaction?.channel)}`}
                          >
                            <span className="flex items-center gap-1">
                              {getChannelIcon(conversation.interaction?.channel)}
                              {getChannelName(conversation.interaction?.channel)}
                            </span>
                          </Badge>
                        </div>
                        <Badge 
                          variant={conversation.resolved ? "default" : "secondary"} 
                          className={`text-xs ${conversation.resolved ? 'bg-green-800 text-green-200' : 'bg-gray-700 text-gray-300'}`}
                        >
                          {conversation.resolved ? "Resolved" : "Active"}
                        </Badge>
                      </div>
                      
                      <div className="mb-3">
                        <p className="text-sm text-gray-300 line-clamp-2 leading-relaxed">
                          {conversation.interaction?.question?.length > 80 
                            ? `${conversation.interaction.question.substring(0, 80)}...`
                            : conversation.interaction?.question || "No message"}
                        </p>
                      </div>
                      
                      <div className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-1 text-gray-500">
                          <Clock className="w-3 h-3" />
                          <span>{new Date(conversation.created_at).toLocaleDateString('en-US', { 
                            month: 'short', 
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}</span>
                        </div>
                        {conversation.interaction?.answer && (
                          <div className="flex items-center gap-1 text-green-400">
                            <MessageSquare className="w-3 h-3" />
                            <span>AI Responded</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <Card className="bg-gray-800 border-gray-700">
                    <CardHeader>
                      <CardTitle className="text-sm text-gray-200">Conversation History</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <p className="text-sm text-gray-400">
                        Start a conversation to see your chat history here. All conversations are automatically saved.
                      </p>
                      <div className="space-y-1">
                        <div className="text-xs text-gray-500">• Messages are saved automatically</div>
                        <div className="text-xs text-gray-500">• Access previous conversations anytime</div>
                        <div className="text-xs text-gray-500">• Continue where you left off</div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="tickets" className="mt-4">
            <ScrollArea className="h-[calc(100vh-200px)]">
              <div className="space-y-3">
                {tickets.length > 0 ? (
                  tickets.map((ticket: UserTicket) => (
                    <div
                      key={ticket.id}
                      className="bg-gray-800 border border-gray-600 rounded-lg p-4 hover:shadow-md transition-all duration-200"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${
                            ticket.status === 'resolved' ? 'bg-green-500' : 'bg-orange-500'
                          }`} />
                          <span className="text-sm font-semibold text-gray-200">
                            TICKET-{String(ticket.id).padStart(3, '0')}
                          </span>
                        </div>
                        <div className="flex items-center gap-1">
                          {ticket.status === 'resolved' ? (
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          ) : (
                            <AlertCircle className="w-4 h-4 text-orange-500" />
                          )}
                          <Badge 
                            variant={ticket.status === 'resolved' ? "default" : "secondary"}
                            className={`text-xs ${
                              ticket.status === 'resolved' 
                                ? 'bg-green-800 text-green-200' 
                                : 'bg-orange-800 text-orange-200'
                            }`}
                          >
                            {ticket.status.toUpperCase()}
                          </Badge>
                        </div>
                      </div>
                      
                      <div className="mb-3">
                        <p className="text-sm text-gray-300 leading-relaxed">
                          {ticket.topic}
                        </p>
                      </div>
                      
                      <div className="flex items-center justify-between text-xs mb-3">
                        <div className="flex items-center gap-1 text-gray-500">
                          <Clock className="w-3 h-3" />
                          <span>Created: {new Date(ticket.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>

                      {ticket.status === 'open' ? (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => markTicketAsResolved(ticket.id)}
                          className="w-full text-xs bg-green-900 border-green-700 text-green-200 hover:bg-green-800"
                        >
                          Mark as Resolved
                        </Button>
                      ) : (
                        <div className="w-full text-center">
                          <span className="text-xs text-green-400 font-medium">✓ Resolved</span>
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <Card className="bg-gray-800 border-gray-700">
                    <CardHeader>
                      <CardTitle className="text-sm text-gray-200">Support Tickets</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <p className="text-sm text-gray-400">
                        No support tickets yet. If the AI assistant can't resolve your query, you will be given an option to create a ticket.
                      </p>
                      <div className="space-y-1">
                        <div className="text-xs text-gray-500">• Tickets help you get human assistance</div>
                        <div className="text-xs text-gray-500">• Track the status of your requests</div>
                        <div className="text-xs text-gray-500">• Mark them as resolved when done</div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
