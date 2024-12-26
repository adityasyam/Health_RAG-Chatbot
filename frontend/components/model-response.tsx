// @ts-nocheck

import React from 'react';
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";

const ModelResponse = ({ data }) => {
    const response = data[0];

    return (
        <div className="p-6 space-y-4">
            <Card className="bg-gray-100 p-4">
                <CardContent>
                    <p>{response.content}</p>
                </CardContent>
            </Card>
        </div>
    );
};

export default ModelResponse;
