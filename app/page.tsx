"use client";

import type React from "react";
import { useState } from "react";
import {
  Send,
  Book,
  Languages,
  GraduationCap,
  ChevronDown,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  SidebarProvider,
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarTrigger,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
} from "@/components/ui/sidebar";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  corrections?: {
    original: string;
    corrected: string;
    explanation: string;
  }[];
};

type Language = {
  code: string;
  name: string;
  grammarLinks: {
    title: string;
    url: string;
  }[];
};

export default function LanguageLearningChatbot() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Hello! I'm your language learning assistant. Please select a language and submit some text for me to correct.",
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [selectedLanguage, setSelectedLanguage] = useState<string>("spanish");

  const languages: Record<string, Language> = {
    spanish: {
      code: "es",
      name: "Spanish",
      grammarLinks: [
        { title: "Present Tense Conjugation", url: "#present-tense" },
        { title: "Past Tense (Preterite)", url: "#preterite" },
        { title: "Past Tense (Imperfect)", url: "#imperfect" },
        { title: "Subjunctive Mood", url: "#subjunctive" },
        { title: "Ser vs Estar", url: "#ser-estar" },
        { title: "Por vs Para", url: "#por-para" },
      ],
    },
    french: {
      code: "fr",
      name: "French",
      grammarLinks: [
        { title: "Present Tense Verbs", url: "#present-tense" },
        { title: "Passé Composé", url: "#passe-compose" },
        { title: "Imparfait", url: "#imparfait" },
        { title: "Subjunctive Mood", url: "#subjunctive" },
        { title: "Articles (Le, La, Les)", url: "#articles" },
        { title: "Negation", url: "#negation" },
      ],
    },
    chinese: {
      code: "ch",
      name: "Chinese",
      grammarLinks: [
        { title: "Word Order SVO", url: "#word-order" },
        { title: "Tenses and Time Words", url: "#time-words" },
        { title: "Particles", url: "#particles" },
        { title: "Measure Words", url: "#measure-words" },
        { title: "Topic Comment Structure", url: "#topic-comment" },
        { title: "Coverbs", url: "#coverbs" },
      ],
    },
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputText,
    };

    setMessages((prev) => [...prev, userMessage]);

    try {
      const res = await fetch("http://localhost:8000/send", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: inputText,
          language: selectedLanguage,
        }),
      });
      if (!res.ok) {
        throw new Error("Failed to fetch response");
      }
      const data = await res.json();
      let content = data.reply;
      if (selectedLanguage === "chinese") {
        content = content.replace(/(\d+\.\s)/g, "\n$1");
      }
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: content,
        corrections: data.corrections,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error:", error);
      // Add error message to chat
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: "assistant",
          content: "Sorry, there was an error processing your message.",
        },
      ]);
    }

    setInputText("");
  };

  return (
    <SidebarProvider>
      <div className="flex h-screen bg-background">
        <Sidebar>
          <SidebarHeader className="border-b">
            <div className="flex items-center gap-2 px-2">
              <Book className="h-6 w-6" />
              <h2 className="text-lg font-semibold">Language Resources</h2>
            </div>
          </SidebarHeader>
          <SidebarContent>
            <SidebarGroup>
              <SidebarGroupLabel>
                <div className="flex items-center gap-2">
                  <GraduationCap className="h-4 w-4" />
                  <span>{languages[selectedLanguage]?.name} Grammar</span>
                </div>
              </SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {languages[selectedLanguage]?.grammarLinks.map((link) => (
                    <SidebarMenuItem key={link.title}>
                      <SidebarMenuButton asChild>
                        <a href={link.url}>
                          <ChevronDown className="h-4 w-4" />
                          <span>{link.title}</span>
                        </a>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>
        </Sidebar>

        <div className="flex flex-1 flex-col">
          <header className="border-b p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <SidebarTrigger />
                <h1 className="text-xl font-bold">
                  Language Learning Assistant
                </h1>
              </div>
              <div className="flex items-center gap-2">
                <Languages className="h-5 w-5" />
                <Select
                  value={selectedLanguage}
                  onValueChange={setSelectedLanguage}
                >
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Select Language" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="spanish">Spanish</SelectItem>
                    <SelectItem value="french">French</SelectItem>
                    <SelectItem value="chinese">Chinese</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </header>

          <main className="flex-1 overflow-auto p-4">
            <div className="mx-auto max-w-3xl space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`rounded-lg p-4 max-w-[80%] ${
                      message.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted"
                    }`}
                    style={{ whiteSpace: "pre-wrap" }}
                  >
                    <p>{message.content}</p>
                    {message.corrections && (
                      <div className="mt-3 space-y-2">
                        {message.corrections.map((correction, index) => (
                          <div
                            key={index}
                            className="rounded border p-2 bg-background"
                          >
                            <div className="flex flex-col gap-1">
                              <div className="text-sm text-destructive line-through">
                                {correction.original}
                              </div>
                              <div className="text-sm text-green-600 font-medium">
                                {correction.corrected}
                              </div>
                              <div className="text-xs text-muted-foreground mt-1">
                                {correction.explanation}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </main>

          <footer className="border-t p-4">
            <form onSubmit={handleSubmit} className="mx-auto max-w-3xl">
              <div className="flex gap-2">
                <Textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder={`Type something in ${languages[selectedLanguage]?.name} for correction...`}
                  className="min-h-[80px] flex-1"
                />
                <Button type="submit" size="icon" className="h-auto">
                  <Send className="h-4 w-4" />
                  <span className="sr-only">Send</span>
                </Button>
              </div>
            </form>
          </footer>
        </div>
      </div>
    </SidebarProvider>
  );
}
