import { 
  BookOpen, 
  Highlighter, 
  MessageCircle, 
  PenLine, 
  Link2, 
  Footprints, 
  HelpCircle, 
  Users, 
  Video, 
  ThumbsUp, 
  Palette, 
  FileText, 
  GraduationCap, 
  Mail, 
  Presentation, 
  BookMarked, 
  Lightbulb,
  type LucideIcon
} from 'lucide-react';

/**
 * 활동 유형별 탕감 포인트 정의
 */
export const ACTIVITY_POINTS: Record<string, number> = {
  read: 10,           // 독서 (일부)
  highlight: 20,      // 밑줄/하이라이트
  feeling: 20,        // 감상 기록
  diary: 25,          // 독서 일지
  writing: 30,        // 서평 작성
  quiz: 30,           // 퀴즈/테스트
  recommend: 30,      // 추천하기
  visual: 35,         // 시각화 (마인드맵, 스케치)
  blog: 35,           // 블로그 포스팅
  connect: 40,        // 다른 지식과 연결
  discussion: 40,     // 토론 참여
  letter: 40,         // 작가에게 편지
  study: 45,          // 스터디 참여
  action: 50,         // 실천/적용
  video: 50,          // 영상 제작
  presentation: 50,   // 발표/프레젠테이션
  project: 60,        // 프로젝트 적용
};

/**
 * 활동 유형 정의 (Lucide 아이콘 포함)
 */
export const ACTIVITY_TYPES: ReadonlyArray<{
  type: string;
  icon: LucideIcon;
  label: string;
  points: number;
  color: string;
}> = [
  { type: 'read', icon: BookOpen, label: '한독/부분독', points: 10, color: 'blue' },
  { type: 'highlight', icon: Highlighter, label: '밑줄/메모 기록', points: 20, color: 'yellow' },
  { type: 'feeling', icon: MessageCircle, label: '느낌/생각 정리', points: 20, color: 'pink' },
  { type: 'writing', icon: PenLine, label: '글쓰기/독후감', points: 30, color: 'indigo' },
  { type: 'connect', icon: Link2, label: '다른 책과 연결', points: 40, color: 'emerald' },
  { type: 'action', icon: Footprints, label: '일상 실천', points: 50, color: 'green' },
  { type: 'quiz', icon: HelpCircle, label: '퀴즈 만들기', points: 30, color: 'cyan' },
  { type: 'discussion', icon: Users, label: '독서 토론 모임', points: 40, color: 'sky' },
  { type: 'video', icon: Video, label: '북 리뷰/요약 영상', points: 50, color: 'red' },
  { type: 'recommend', icon: ThumbsUp, label: '책 추천/설명', points: 30, color: 'teal' },
  { type: 'visual', icon: Palette, label: '비주얼 노트/마인드맵', points: 35, color: 'orange' },
  { type: 'blog', icon: FileText, label: '블로그/SNS 포스팅', points: 35, color: 'lime' },
  { type: 'study', icon: GraduationCap, label: '스터디 그룹 운영', points: 45, color: 'fuchsia' },
  { type: 'letter', icon: Mail, label: '저자에게 편지', points: 40, color: 'violet' },
  { type: 'presentation', icon: Presentation, label: '발표/강연 자료', points: 50, color: 'amber' },
  { type: 'diary', icon: BookMarked, label: '북 다이어리/독서 일지', points: 25, color: 'purple' },
  { type: 'project', icon: Lightbulb, label: '프로젝트/사이드 프로젝트', points: 60, color: 'rose' },
];

