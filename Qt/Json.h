#ifndef JNC_JSON_H
#define JNC_JSON_H
#include <QString>
#include <QJsonDocument>

namespace jnc
{
    class Json
    {
    private:
        Json() = delete;

    public:
        static void dump(const QString& fileName, const QJsonDocument& jsonDoc);
        static QJsonDocument load(const QString& fileName);

        // We don't need dumps() and loads() because QJsonDocument already provides
        // fromJson() and toJson() and they're good enough.
    };
}

#endif // JSON_H
