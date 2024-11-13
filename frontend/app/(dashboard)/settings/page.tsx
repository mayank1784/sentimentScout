"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";

const formSchema = z.object({
  current_password: z.string().min(6),
  new_password: z.string().min(6),
  new_email: z.string().email(),
});

export default function SettingsPage() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      current_password: "",
      new_password: "",
      new_email: "",
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      // Update email if provided
      if (values.new_email) {
        const emailResponse = await fetch("/update_email", {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            new_email: values.new_email,
            password: values.current_password,
          }),
        });

        if (!emailResponse.ok) {
          const emailData = await emailResponse.json();
          throw new Error(emailData.message || "Failed to update email");
        }
        toast.success("Email updated successfully");
      }

      // Update password if provided
      if (values.new_password) {
        const passwordResponse = await fetch("/update_password", {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            current_password: values.current_password,
            new_password: values.new_password,
          }),
        });

        if (!passwordResponse.ok) {
          const passwordData = await passwordResponse.json();
          throw new Error(passwordData.message || "Failed to update password");
        }
        toast.success("Password updated successfully");
      }

      form.reset();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Update failed");
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Account Settings</h1>
        <p className="text-gray-600">Update your account information</p>
      </div>

      <Card className="max-w-2xl p-6">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
            <FormField
              control={form.control}
              name="current_password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Current Password</FormLabel>
                  <FormControl>
                    <Input type="password" placeholder="Enter current password" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="new_password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>New Password</FormLabel>
                  <FormControl>
                    <Input type="password" placeholder="Enter new password" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="new_email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>New Email</FormLabel>
                  <FormControl>
                    <Input type="email" placeholder="Enter new email" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button type="submit">Update Settings</Button>
          </form>
        </Form>
      </Card>
    </div>
  );
}