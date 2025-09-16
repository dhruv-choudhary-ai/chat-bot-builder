"use client"

import { useEffect, useRef, useState } from "react"
import { useAuth } from "@/hooks/use-auth.ts"
import { apiFetch } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { ConversationSidebar } from "@/components/chat/conversation-sidebar"

type Message = {
  id: string
  who: "user" | "ai"
  text: string
  timestamp: Date
  showFlagButton?: boolean
  showNewChatButton?: boolean
  ticketId?: number
  showResolveButton?: boolean
}

export default function ChatPage() {
  const { token, isAuthenticated, logout, loading } = useAuth("user")
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [ticketTopic, setTicketTopic] = useState("")
  const [showTicketDialog, setShowTicketDialog] = useState(false)
  const [showFlagDialog, setShowFlagDialog] = useState(false)
  const [flagTopic, setFlagTopic] = useState("")
  const [showTicketSupport, setShowTicketSupport] = useState(false)
  const [userTickets, setUserTickets] = useState<any[]>([])
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null)
  const [refreshSidebar, setRefreshSidebar] = useState(0)
  const [availableBots, setAvailableBots] = useState<any[]>([])
  const [selectedBotId, setSelectedBotId] = useState<number | null>(null)
  const [showBotSelector, setShowBotSelector] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // wait for auth to finish loading before redirecting
    if (!loading && !isAuthenticated) {
      window.location.href = "/login"
    }
  }, [isAuthenticated, loading])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  useEffect(() => {
    if (token) {
      fetchUserTickets()
      fetchAvailableBots()
    }
  }, [token, refreshSidebar])

  const fetchAvailableBots = async () => {
    if (!token) return
    try {
      const bots = await apiFetch<any[]>("/users/me/bots", {}, token)
      setAvailableBots(bots)
      // Auto-select first bot if available
      if (bots.length > 0 && !selectedBotId) {
        setSelectedBotId(bots[0].id)
      }
    } catch (error) {
      console.error("Failed to fetch available bots:", error)
    }
  }

  useEffect(() => {
    // Reload current conversation when tickets change (to update button states)
    if (currentConversationId && userTickets.length > 0) {
      handleConversationSelect(currentConversationId)
    }
  }, [userTickets])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showTicketSupport && !(event.target as Element).closest('.ticket-support-dropdown')) {
        setShowTicketSupport(false)
      }
      if (showBotSelector && !(event.target as Element).closest('.bot-selector-dropdown')) {
        setShowBotSelector(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showTicketSupport, showBotSelector])

  const fetchUserTickets = async () => {
    if (!token) return
    try {
      const tickets = await apiFetch<any[]>("/users/me/tickets", {}, token)
      setUserTickets(tickets)
    } catch (error) {
      console.error("Failed to fetch user tickets:", error)
    }
  }

  const handleConversationSelect = async (conversationId: string) => {
    setCurrentConversationId(conversationId)
    
    try {
      // Get the conversation data from the conversation sidebar's conversations list
      // Since each conversation contains one Q&A pair, we'll convert it to messages
      const response = await apiFetch<any[]>(
        `/users/conversations`,
        {},
        token || undefined
      )
      
      const selectedConversation = response.find((conv: any) => conv.id.toString() === conversationId)
      
      if (selectedConversation && selectedConversation.interaction) {
        console.log('Debug: Selected conversation:', selectedConversation)
        console.log('Debug: Interaction object:', selectedConversation.interaction)
        console.log('Debug: Answer type:', typeof selectedConversation.interaction.answer)
        console.log('Debug: Answer value:', selectedConversation.interaction.answer)
        
        const conversationMessages: Message[] = []
        
        // Add the user's question
        if (selectedConversation.interaction.question) {
          // Ensure the question is a string, not an object
          let questionText = selectedConversation.interaction.question
          if (typeof questionText !== 'string') {
            // If it's an object, try to extract the text or stringify it properly
            if (questionText && typeof questionText === 'object') {
              questionText = questionText.question || questionText.text || JSON.stringify(questionText)
            } else {
              questionText = String(questionText)
            }
          }
          
          conversationMessages.push({
            id: `${conversationId}-question`,
            who: "user",
            text: questionText,
            timestamp: new Date(selectedConversation.created_at),
            showFlagButton: false,
            showNewChatButton: false,
            showResolveButton: false,
            ticketId: undefined
          })
        }
        
        // Add the AI's answer
        if (selectedConversation.interaction.answer) {
          // Ensure the answer is a string, not an object
          let answerText = selectedConversation.interaction.answer
          if (typeof answerText !== 'string') {
            // If it's an object, try to extract the text or stringify it properly
            if (answerText && typeof answerText === 'object') {
              answerText = answerText.answer || answerText.text || JSON.stringify(answerText)
            } else {
              answerText = String(answerText)
            }
          } else if (answerText.startsWith('{') && answerText.endsWith('}')) {
            // Check if it's a stringified JSON that needs parsing
            try {
              const parsed = JSON.parse(answerText)
              if (parsed && typeof parsed === 'object') {
                answerText = parsed.answer || parsed.text || answerText
              }
            } catch (e) {
              // If parsing fails, keep the original string
              console.warn('Failed to parse stringified JSON:', e)
            }
          }
          
          const aiMessage: Message = {
            id: `${conversationId}-answer`, 
            who: "ai",
            text: answerText,
            timestamp: new Date(selectedConversation.created_at),
            showFlagButton: answerText.toLowerCase().includes('flag this for human assistance'),
            showNewChatButton: false,
            showResolveButton: false,
            ticketId: undefined
          }
          
          // Check if this message mentions a ticket ID or if there are tickets for this conversation
          const ticketMatch = selectedConversation.interaction.answer.match(/Ticket #(\d+)/i)
          let hasTicket = false
          let ticketId: number | undefined
          let isTicketResolved = false
          
          if (ticketMatch) {
            // Direct ticket mention in message
            ticketId = parseInt(ticketMatch[1])
            hasTicket = true
            const ticket = userTickets.find(t => t.id === ticketId)
            isTicketResolved = ticket ? ticket.status === 'resolved' : false
          } else {
            // Check for related tickets by timestamp (within 1 minute of conversation)
            const conversationTickets = userTickets.filter(ticket => 
              new Date(ticket.created_at).getTime() >= new Date(selectedConversation.created_at).getTime() - 60000 &&
              new Date(ticket.created_at).getTime() <= new Date(selectedConversation.created_at).getTime() + 60000
            )
            
            if (conversationTickets.length > 0) {
              const latestTicket = conversationTickets[conversationTickets.length - 1]
              ticketId = latestTicket.id
              hasTicket = true
              isTicketResolved = latestTicket.status === 'resolved'
            }
          }
          
          // Show buttons if there's a ticket associated with this conversation
          if (hasTicket && ticketId) {
            aiMessage.ticketId = ticketId
            aiMessage.showNewChatButton = true
            aiMessage.showResolveButton = !isTicketResolved
            // Hide flag button since a ticket already exists
            aiMessage.showFlagButton = false
            
            // Update message text to include ticket ID if not already present
            if (!ticketMatch && !isTicketResolved) {
              aiMessage.text = aiMessage.text + ` (Ticket #${ticketId})`
            } else if (!ticketMatch && isTicketResolved) {
              aiMessage.text = aiMessage.text + ` (Resolved Ticket #${ticketId})`
            }
          }
          
          conversationMessages.push(aiMessage)
        }
        
        setMessages(conversationMessages)
      } else {
        setMessages([])
      }
    } catch (error) {
      console.error("Failed to load conversation:", error)
      setMessages([])
    }
  }

  const handleNewConversation = () => {
    setCurrentConversationId(null)
    setMessages([])
  }

    const sendMessage = async () => {
    if (!inputText.trim() || !token || !selectedBotId) {
      if (!selectedBotId) {
        alert("Please select a bot first!")
      }
      return
    }

    // If we're viewing an old conversation, start a new one
    if (currentConversationId) {
      setCurrentConversationId(null)
      setMessages([]) // Clear old messages
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      who: "user",
      text: inputText.trim(),
      timestamp: new Date(),
      showFlagButton: false,
      showNewChatButton: false,
      showResolveButton: false,
      ticketId: undefined
    }

    setMessages(prev => [...prev, userMessage])
    setInputText("")
    setIsLoading(true)

    try {
      const response = await apiFetch<{ answer: string }>(
        `/bots/${selectedBotId}/query`,
        {
          method: "POST",
          body: JSON.stringify({ question: inputText.trim() }),
        },
        token || undefined,
      )

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        who: "ai",
        text: response.answer || "I'm sorry, I couldn't process your request.",
        timestamp: new Date(),
        showFlagButton: response.answer?.toLowerCase().includes('flag this for human assistance') || false,
        showNewChatButton: false,
        showResolveButton: false,
        ticketId: undefined
      }

      setMessages(prev => [...prev, aiMessage])
      
      // Refresh sidebar to show new conversation
      setRefreshSidebar(prev => prev + 1)
    } catch (error) {
      console.error("Failed to get AI response:", error)
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        who: "ai",
        text: "I'm currently unable to process your request due to technical issues. Please try again later or contact support.",
        timestamp: new Date(),
        showFlagButton: false,
        showNewChatButton: false,
        showResolveButton: false,
        ticketId: undefined
      }

      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const raiseTicket = async () => {
    if (!ticketTopic.trim() || !token) return

    try {
      const response = await apiFetch<{ id: number }>(
        "/users/me/tickets",
        {
          method: "POST",
          body: JSON.stringify({ topic: ticketTopic.trim() }),
        },
        token || undefined,
      )

      alert(`Ticket raised successfully! Ticket ID: ${response.id}`)
      setTicketTopic("")
      setShowTicketDialog(false)
      
      // Refresh sidebar and tickets list to show new ticket
      setRefreshSidebar(prev => prev + 1)
      fetchUserTickets()
    } catch (error) {
      console.error("Failed to raise ticket:", error)
      alert("Failed to raise ticket. Please try again.")
    }
  }

  const flagForAssistance = async () => {
    if (!flagTopic.trim() || !token) return

    try {
      const response = await apiFetch<{ id: number }>(
        "/users/me/tickets",
        {
          method: "POST",
          body: JSON.stringify({ topic: flagTopic.trim() }),
        },
        token || undefined,
      )

      // Store the created ticket ID for confirmation message
      const ticketId = response.id

      // Add confirmation message to chat
      const confirmationMessage: Message = {
        id: (Date.now() + 2).toString(),
        who: "ai",
        text: `Your query has been flagged for human assistance (Ticket #${ticketId}). You can track the status in the Support Tickets section.`,
        timestamp: new Date(),
        showFlagButton: false,
        showNewChatButton: true,
        ticketId: ticketId,
        showResolveButton: true
      }

      // Hide the flag button from the original message that had it
      setMessages(prev => prev.map(msg => 
        msg.showFlagButton ? { ...msg, showFlagButton: false } : msg
      ).concat(confirmationMessage))
      setFlagTopic("")
      setShowFlagDialog(false)
      
      // Refresh sidebar to show the change (both conversations and tickets)
      setRefreshSidebar(prev => prev + 1)
      
      // Fetch updated tickets and wait for them to load
      await fetchUserTickets()
      
      // The useEffect will automatically reload the conversation when userTickets updates
    } catch (error) {
      console.error("Failed to flag for assistance:", error)
      alert("Failed to flag for assistance. Please try again.")
    }
  }

  const resolveTicket = async (ticketId: number) => {
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
        
        // Update the message to remove resolve button
        setMessages(prev => prev.map(msg => 
          msg.ticketId === ticketId 
            ? { ...msg, showResolveButton: false, text: msg.text.replace('(Ticket #', '(Resolved Ticket #') }
            : msg
        ))
        
        // Refresh sidebar and tickets to show the change
        setRefreshSidebar(prev => prev + 1)
        await fetchUserTickets()
        
        // Force reload current conversation to update button states
        if (currentConversationId) {
          handleConversationSelect(currentConversationId)
        }
      } catch (error) {
        console.error("Failed to resolve ticket:", error)
        alert("Failed to resolve ticket. Please try again.")
      }
    }
  }

  if (loading) {
    return null
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="h-screen bg-gray-900 text-white flex overflow-hidden">
      {/* Conversation Sidebar */}
      <ConversationSidebar
        currentConversationId={currentConversationId || undefined}
        onConversationSelect={handleConversationSelect}
        onNewConversation={handleNewConversation}
        refreshKey={refreshSidebar}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-full">
        {/* Minimal Header */}
        <header className="bg-gray-800 border-b border-gray-700 p-4">
          <div className="flex items-center justify-between max-w-4xl mx-auto">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-sm">AI</span>
              </div>
              <h1 className="text-xl font-semibold text-white">AI LifeBOT</h1>
              {currentConversationId && (
                <Badge variant="outline" className="ml-2 border-gray-600 text-gray-300">
                  Conversation #{currentConversationId}
                </Badge>
              )}
              {selectedBotId && (
                <Badge variant="outline" className="ml-2 border-blue-600 text-blue-300">
                  Bot: {availableBots.find(bot => bot.id === selectedBotId)?.name || selectedBotId}
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-3">
              {/* Bot Selector */}
              <div className="relative bot-selector-dropdown">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowBotSelector(!showBotSelector)}
                  className="border-gray-600 text-gray-300 hover:bg-gray-700"
                >
                  Select Bot
                  <span className="ml-2">▼</span>
                </Button>
                
                {showBotSelector && (
                  <div className="absolute top-full left-0 mt-2 w-64 bg-gray-800 border border-gray-600 rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto">
                    <div className="p-2">
                      <h3 className="font-medium text-gray-200 text-sm mb-2">Available Bots</h3>
                      {availableBots.length > 0 ? (
                        availableBots.map((bot) => (
                          <button
                            key={bot.id}
                            onClick={() => {
                              setSelectedBotId(bot.id)
                              setShowBotSelector(false)
                              // Clear current conversation when switching bots
                              setCurrentConversationId(null)
                              setMessages([])
                            }}
                            className={`w-full text-left p-2 rounded text-sm transition-colors ${
                              selectedBotId === bot.id
                                ? 'bg-gray-700 text-white'
                                : 'text-gray-300 hover:bg-gray-700'
                            }`}
                          >
                            <div className="font-medium">{bot.name}</div>
                            <div className="text-xs text-gray-400">{bot.bot_type}</div>
                          </button>
                        ))
                      ) : (
                        <div className="p-2 text-gray-400 text-sm">No bots available</div>
                      )}
                    </div>
                  </div>
                )}
              </div>
              <div className="relative ticket-support-dropdown">
                <Button
                  variant="outline"
                  onClick={() => setShowTicketSupport(!showTicketSupport)}
                  className="border-gray-600 text-gray-300 hover:bg-gray-700"
                >
                  Ticket Support
                  <span className="ml-2">▼</span>
                </Button>
                
                {showTicketSupport && (
                  <div className="absolute top-full right-0 mt-2 w-80 bg-gray-800 border border-gray-600 rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
                    <div className="p-4 border-b border-gray-600">
                      <div className="flex items-center justify-between">
                        <h3 className="font-medium text-gray-100">Support Tickets</h3>
                        <Button
                          size="sm"
                          onClick={() => {
                            setShowTicketSupport(false)
                            setShowTicketDialog(true)
                          }}
                          className="text-xs"
                        >
                          New Ticket
                        </Button>
                      </div>
                    </div>
                    
                    <div className="max-h-64 overflow-y-auto">
                      {userTickets.length > 0 ? (
                        userTickets.map((ticket) => (
                          <div key={ticket.id} className="p-3 border-b border-gray-700 hover:bg-gray-700">
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex items-center gap-2">
                                <div className={`w-2 h-2 rounded-full ${
                                  ticket.status === 'resolved' ? 'bg-green-500' : 'bg-orange-500'
                                }`} />
                                <span className="text-sm font-medium text-gray-100">
                                  TICKET-{String(ticket.id).padStart(3, '0')}
                                </span>
                              </div>
                              <Badge 
                                variant={ticket.status === 'resolved' ? "default" : "secondary"}
                                className={`text-xs ${
                                  ticket.status === 'resolved' 
                                    ? 'bg-green-100 text-green-700' 
                                    : 'bg-orange-100 text-orange-700'
                                }`}
                              >
                                {ticket.status.toUpperCase()}
                              </Badge>
                            </div>
                            <p className="text-sm text-gray-300 mb-2">{ticket.topic}</p>
                            <p className="text-xs text-gray-500">
                              {new Date(ticket.created_at).toLocaleDateString()}
                            </p>
                            {ticket.status === 'open' && (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => {
                                  setShowTicketSupport(false)
                                  resolveTicket(ticket.id)
                                }}
                                className="mt-2 text-xs bg-green-800 border-green-600 text-green-200 hover:bg-green-700"
                              >
                                Mark as Resolved
                              </Button>
                            )}
                          </div>
                        ))
                      ) : (
                        <div className="p-4 text-center text-gray-400">
                          <p className="text-sm">No tickets created yet</p>
                          <p className="text-xs mt-1">Create a ticket when you need human assistance</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
              <Button
                variant="outline"
                onClick={logout}
                className="border-gray-600 text-gray-300 hover:bg-gray-700"
              >
                Logout
              </Button>
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col h-full overflow-hidden">
          <ScrollArea className="flex-1 p-4 overflow-y-auto">
            <div className="max-w-4xl mx-auto space-y-6 min-h-full">
              {messages.length === 0 && !currentConversationId && (
                <div className="text-center py-12">
                  {/* <div className="text-6xl mb-4">🤖</div> */}
                  {!selectedBotId ? (
                    <>
                      <h2 className="text-2xl font-semibold mb-2 text-white">Welcome to AI LifeBOT</h2>
                      <p className="text-gray-400 mb-4">Please select a bot from the dropdown above to start chatting.</p>
                      <Button
                        variant="outline"
                        onClick={() => setShowBotSelector(true)}
                        className="border-gray-600 text-gray-300 hover:bg-gray-700"
                      >
                        Select a Bot
                      </Button>
                    </>
                  ) : (
                    <>
                      <h2 className="text-2xl font-semibold mb-2 text-white">Welcome to AI LifeBOT</h2>
                      <p className="text-gray-400">Ask me anything and I'll help you with intelligent, AI-powered responses.</p>
                      <p className="text-gray-500 text-sm mt-2">
                        Currently using: {availableBots.find(bot => bot.id === selectedBotId)?.name}
                      </p>
                    </>
                  )}
                </div>
              )}

              {messages.length === 0 && currentConversationId && (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">💬</div>
                  <h2 className="text-2xl font-semibold mb-2 text-white">Conversation Loaded</h2>
                  <p className="text-gray-400">This conversation has no messages yet. Start chatting!</p>
                </div>
              )}

              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.who === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[70%] rounded-lg px-4 py-3 ${
                      message.who === "user"
                        ? "bg-gray-700 text-white"
                        : "bg-gray-800 text-gray-100"
                    }`}
                  >
                    <p className="text-sm">{message.text}</p>
                    <p className="text-xs opacity-70 mt-2">
                      {message.timestamp.toLocaleString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: true
                      })}
                    </p>
                    {(message.showFlagButton || message.showNewChatButton || message.showResolveButton) && (
                      <div className="mt-3 pt-2 border-t border-gray-600 space-y-2">
                        {message.showFlagButton && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setShowFlagDialog(true)}
                            className="text-xs bg-orange-900 border-orange-700 text-orange-200 hover:bg-orange-800 mr-2"
                          >
                            Flag for Human Assistance
                          </Button>
                        )}
                        <div className="flex gap-2">
                          {message.showNewChatButton && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={handleNewConversation}
                              className="text-xs bg-green-900 border-green-700 text-green-200 hover:bg-green-800"
                            >
                              Start New Conversation
                            </Button>
                          )}
                          {message.showResolveButton && message.ticketId && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => resolveTicket(message.ticketId!)}
                              className="text-xs bg-gray-700 border-gray-600 text-gray-200 hover:bg-gray-600"
                            >
                              Mark as Resolved
                            </Button>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-800 rounded-lg px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          {/* Input Area */}
          <div className="border-t border-gray-700 p-4 bg-gray-800 flex-shrink-0">
            <div className="max-w-4xl mx-auto">
              <div className="flex gap-3">
                <Input
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={selectedBotId ? "Ask me anything..." : "Please select a bot first..."}
                  className="flex-1 bg-gray-700 border-gray-600 text-white placeholder:text-gray-400"
                  disabled={isLoading || !selectedBotId}
                />
                <Button
                  onClick={sendMessage}
                  disabled={!inputText.trim() || isLoading || !selectedBotId}
                  className="bg-gray-600 hover:bg-gray-500 px-6"
                >
                  {isLoading ? "Sending..." : "Send"}
                </Button>
              </div>
              <p className="text-xs text-gray-500 mt-2 text-center">
                Press Enter to send, Shift+Enter for new line
              </p>
            </div>
          </div>
        </div>

        {/* Ticket Dialog */}
        {showTicketDialog && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full">
              <h3 className="text-lg font-semibold mb-4 text-white">Raise a Ticket</h3>
              <Input
                value={ticketTopic}
                onChange={(e) => setTicketTopic(e.target.value)}
                placeholder="Describe your issue..."
                className="mb-4 bg-gray-700 border-gray-600 text-white placeholder:text-gray-400"
              />
              <div className="flex gap-2">
                <Button onClick={raiseTicket} disabled={!ticketTopic.trim()}>
                  Submit
                </Button>
                <Button variant="outline" onClick={() => setShowTicketDialog(false)}>
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Flag for Assistance Dialog */}
        {showFlagDialog && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-gray-800/95 backdrop-blur-md rounded-lg p-6 max-w-md w-full shadow-xl border border-gray-600">
              <h3 className="text-lg font-semibold mb-4 text-white">Flag for Human Assistance</h3>
              <p className="text-sm text-gray-400 mb-4">
                Please briefly describe your query in one line:
              </p>
              <Input
                value={flagTopic}
                onChange={(e) => setFlagTopic(e.target.value)}
                placeholder="Brief description of your query..."
                className="mb-4 bg-gray-700 border-gray-600 text-white placeholder:text-gray-400"
              />
              <div className="flex gap-2">
                <Button onClick={flagForAssistance} disabled={!flagTopic.trim()}>
                  Flag for Assistance
                </Button>
                <Button variant="outline" onClick={() => setShowFlagDialog(false)}>
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

